// Package pb implements a minimal decoder for the EPICS Archiver Appliance
// "pbraw" protobuf stream format returned by the data retrieval API
// (see http://<host>/retrieval/data/getData.raw), mirroring the field
// layout of EPICSEvent.proto used by the Python implementation
// (main/data/pb/EPICSEvent_pb2.py). It intentionally avoids depending on a
// generated protobuf package and instead parses the wire format directly,
// since only a small, well-known set of messages needs to be understood.
package pb

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"math"
)

// PayloadType mirrors EPICS.PayloadType from EPICSEvent.proto.
type PayloadType int32

const (
	ScalarString PayloadType = iota
	ScalarShort
	ScalarFloat
	ScalarEnum
	ScalarByte
	ScalarInt
	ScalarDouble
	WaveformString
	WaveformShort
	WaveformFloat
	WaveformEnum
	WaveformByte
	WaveformInt
	WaveformDouble
	V4GenericBytes
)

// PayloadInfo is the header message preceding each PV's samples.
type PayloadInfo struct {
	Type    PayloadType
	PVName  string
	Year    int32
	Headers map[string]string
}

// Sample is a single decoded event/sample.
type Sample struct {
	SecondsIntoYear uint32
	Nano            uint32
	Severity        int32
	Status          int32
	// Val holds the decoded value; its concrete type depends on the
	// PayloadType: float64/float32/int64/string/[]byte or a slice of the
	// scalar variant for waveform types.
	Val interface{}
}

// field is a single decoded protobuf wire-format field.
type field struct {
	num      int
	wireType int
	varint   uint64
	fixed64  uint64
	fixed32  uint32
	bytes    []byte
}

const (
	wireVarint  = 0
	wireFixed64 = 1
	wireBytes   = 2
	wireFixed32 = 5
)

func decodeFields(data []byte) ([]field, error) {
	var fields []field
	i := 0
	for i < len(data) {
		tag, n := binary.Uvarint(data[i:])
		if n <= 0 {
			return nil, fmt.Errorf("invalid varint tag at offset %d", i)
		}
		i += n
		f := field{num: int(tag >> 3), wireType: int(tag & 0x7)}
		switch f.wireType {
		case wireVarint:
			v, n := binary.Uvarint(data[i:])
			if n <= 0 {
				return nil, fmt.Errorf("invalid varint value at offset %d", i)
			}
			f.varint = v
			i += n
		case wireFixed64:
			if i+8 > len(data) {
				return nil, fmt.Errorf("truncated fixed64 at offset %d", i)
			}
			f.fixed64 = binary.LittleEndian.Uint64(data[i : i+8])
			i += 8
		case wireBytes:
			l, n := binary.Uvarint(data[i:])
			if n <= 0 {
				return nil, fmt.Errorf("invalid varint length at offset %d", i)
			}
			i += n
			if i+int(l) > len(data) {
				return nil, fmt.Errorf("truncated bytes field at offset %d", i)
			}
			f.bytes = data[i : i+int(l)]
			i += int(l)
		case wireFixed32:
			if i+4 > len(data) {
				return nil, fmt.Errorf("truncated fixed32 at offset %d", i)
			}
			f.fixed32 = binary.LittleEndian.Uint32(data[i : i+4])
			i += 4
		default:
			return nil, fmt.Errorf("unsupported wire type %d at offset %d", f.wireType, i)
		}
		fields = append(fields, f)
	}
	return fields, nil
}

// ParsePayloadInfo decodes an EPICS.PayloadInfo message.
func ParsePayloadInfo(data []byte) (*PayloadInfo, error) {
	fields, err := decodeFields(data)
	if err != nil {
		return nil, err
	}
	info := &PayloadInfo{Headers: map[string]string{}}
	for _, f := range fields {
		switch f.num {
		case 1: // type
			info.Type = PayloadType(f.varint)
		case 2: // pvname
			info.PVName = string(f.bytes)
		case 3: // year
			info.Year = int32(f.varint)
		case 15: // headers (repeated FieldValue)
			sub, err := decodeFields(f.bytes)
			if err != nil {
				return nil, err
			}
			var name, val string
			for _, sf := range sub {
				switch sf.num {
				case 1:
					name = string(sf.bytes)
				case 2:
					val = string(sf.bytes)
				}
			}
			if name != "" {
				info.Headers[name] = val
			}
		}
	}
	return info, nil
}

func decodeZigZag32(v uint64) int32 {
	return int32(int32(v>>1) ^ -int32(v&1))
}

// ParseSample decodes a single sample message according to the given
// PayloadType.
func ParseSample(t PayloadType, data []byte) (*Sample, error) {
	fields, err := decodeFields(data)
	if err != nil {
		return nil, err
	}
	s := &Sample{}
	for _, f := range fields {
		switch f.num {
		case 1:
			s.SecondsIntoYear = uint32(f.varint)
		case 2:
			s.Nano = uint32(f.varint)
		case 3:
			v, err := decodeVal(t, f)
			if err != nil {
				return nil, err
			}
			s.Val = v
		case 4:
			s.Severity = int32(f.varint)
		case 5:
			s.Status = int32(f.varint)
		}
	}
	return s, nil
}

func decodeVal(t PayloadType, f field) (interface{}, error) {
	switch t {
	case ScalarDouble:
		return math.Float64frombits(f.fixed64), nil
	case ScalarFloat:
		return math.Float32frombits(f.fixed32), nil
	case ScalarShort, ScalarEnum:
		return decodeZigZag32(f.varint), nil
	case ScalarInt:
		return int32(f.varint), nil
	case ScalarString:
		return string(f.bytes), nil
	case ScalarByte:
		return f.bytes, nil
	case WaveformDouble:
		return decodePackedFixed64(f.bytes, func(b uint64) interface{} { return math.Float64frombits(b) })
	case WaveformFloat:
		return decodePackedFixed32(f.bytes, func(b uint32) interface{} { return math.Float32frombits(b) })
	case WaveformShort, WaveformEnum:
		return decodePackedVarint(f.bytes, func(v uint64) interface{} { return decodeZigZag32(v) })
	case WaveformInt:
		return decodePackedVarint(f.bytes, func(v uint64) interface{} { return int32(v) })
	case WaveformString:
		// repeated string fields aren't packed; when val is repeated the
		// bytes here represent a single element, callers accumulate them.
		return string(f.bytes), nil
	case WaveformByte, V4GenericBytes:
		return f.bytes, nil
	default:
		return nil, fmt.Errorf("unsupported payload type: %d", t)
	}
}

func decodePackedFixed64(data []byte, conv func(uint64) interface{}) ([]interface{}, error) {
	if len(data)%8 != 0 {
		return nil, fmt.Errorf("invalid packed fixed64 length %d", len(data))
	}
	out := make([]interface{}, 0, len(data)/8)
	for i := 0; i < len(data); i += 8 {
		out = append(out, conv(binary.LittleEndian.Uint64(data[i:i+8])))
	}
	return out, nil
}

func decodePackedFixed32(data []byte, conv func(uint32) interface{}) ([]interface{}, error) {
	if len(data)%4 != 0 {
		return nil, fmt.Errorf("invalid packed fixed32 length %d", len(data))
	}
	out := make([]interface{}, 0, len(data)/4)
	for i := 0; i < len(data); i += 4 {
		out = append(out, conv(binary.LittleEndian.Uint32(data[i:i+4])))
	}
	return out, nil
}

func decodePackedVarint(data []byte, conv func(uint64) interface{}) ([]interface{}, error) {
	var out []interface{}
	i := 0
	for i < len(data) {
		v, n := binary.Uvarint(data[i:])
		if n <= 0 {
			return nil, fmt.Errorf("invalid packed varint at offset %d", i)
		}
		out = append(out, conv(v))
		i += n
	}
	return out, nil
}

// unescape reverses the escaping applied by the archiver appliance to
// protect ESC (0x1b), '\n' and '\r' bytes inside a line, per
// http://<host>/mgmt/ui/help/pb_pbraw.html.
func unescape(line []byte) []byte {
	if !bytes.ContainsRune(line, 0x1b) {
		return line
	}
	out := make([]byte, 0, len(line))
	for i := 0; i < len(line); i++ {
		if line[i] == 0x1b && i+1 < len(line) {
			switch line[i+1] {
			case 0x01:
				out = append(out, 0x1b)
				i++
				continue
			case 0x02:
				out = append(out, 0x0a)
				i++
				continue
			case 0x03:
				out = append(out, 0x0d)
				i++
				continue
			}
		}
		out = append(out, line[i])
	}
	return out
}

// PVData is the decoded result for a single PV, mirroring the
// {'meta': ..., 'data': [...]} structure produced by the Python client.
type PVData struct {
	Info    *PayloadInfo
	Samples []Sample
}

// UnpackRawData decodes the "pbraw" response body for a single PV.
func UnpackRawData(data []byte) (*PVData, error) {
	lines := bytes.Split(data, []byte("\n"))
	var result PVData
	var info *PayloadInfo
	hitHeader := true
	for _, rawLine := range lines {
		line := bytes.TrimSpace(rawLine)
		if len(line) == 0 {
			// A blank line separates blocks in the pbraw stream. Only
			// re-arm header parsing once we've actually recorded a
			// header; otherwise a stray leading blank line (or one
			// immediately following a header, before any samples) must
			// not cause the next content line to be mis-parsed as a
			// second header and silently discard the current one.
			if info != nil {
				hitHeader = true
			}
			continue
		}
		unescaped := unescape(line)
		if hitHeader {
			var err error
			info, err = ParsePayloadInfo(unescaped)
			if err != nil {
				return nil, err
			}
			result.Info = info
			hitHeader = false
			continue
		}
		if info == nil {
			return nil, fmt.Errorf("sample encountered before header")
		}
		sample, err := ParseSample(info.Type, unescaped)
		if err != nil {
			return nil, err
		}
		result.Samples = append(result.Samples, *sample)
	}
	return &result, nil
}
