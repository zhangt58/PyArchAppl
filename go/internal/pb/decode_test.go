package pb

import (
	"bytes"
	"encoding/binary"
	"math"
	"testing"
)

// buf is a tiny protobuf wire-format encoder used only for building test
// fixtures; it intentionally mirrors the subset of encodings decodeFields
// understands.
type buf struct{ b bytes.Buffer }

func (w *buf) tag(num, wireType int) {
	putUvarint(&w.b, uint64(num<<3|wireType))
}

func putUvarint(b *bytes.Buffer, v uint64) {
	var tmp [binary.MaxVarintLen64]byte
	n := binary.PutUvarint(tmp[:], v)
	b.Write(tmp[:n])
}

func (w *buf) varint(num int, v uint64) {
	w.tag(num, wireVarint)
	putUvarint(&w.b, v)
}

func (w *buf) bytesField(num int, v []byte) {
	w.tag(num, wireBytes)
	putUvarint(&w.b, uint64(len(v)))
	w.b.Write(v)
}

func (w *buf) fixed64(num int, v uint64) {
	w.tag(num, wireFixed64)
	var tmp [8]byte
	binary.LittleEndian.PutUint64(tmp[:], v)
	w.b.Write(tmp[:])
}

func TestParsePayloadInfo(t *testing.T) {
	var w buf
	w.varint(1, uint64(ScalarDouble))
	w.bytesField(2, []byte("TEST:pv"))
	w.varint(3, 2021)

	var hv buf
	hv.bytesField(1, []byte("EGU"))
	hv.bytesField(2, []byte("mm"))
	w.bytesField(15, hv.b.Bytes())

	info, err := ParsePayloadInfo(w.b.Bytes())
	if err != nil {
		t.Fatalf("ParsePayloadInfo: %v", err)
	}
	if info.PVName != "TEST:pv" {
		t.Errorf("PVName = %q", info.PVName)
	}
	if info.Type != ScalarDouble {
		t.Errorf("Type = %v, want ScalarDouble", info.Type)
	}
	if info.Year != 2021 {
		t.Errorf("Year = %d, want 2021", info.Year)
	}
	if info.Headers["EGU"] != "mm" {
		t.Errorf("Headers[EGU] = %q, want mm", info.Headers["EGU"])
	}
}

func TestParseSampleScalarDouble(t *testing.T) {
	var w buf
	w.varint(1, 100)
	w.varint(2, 500)
	w.fixed64(3, math.Float64bits(3.14))
	w.varint(4, 0)
	w.varint(5, 0)

	s, err := ParseSample(ScalarDouble, w.b.Bytes())
	if err != nil {
		t.Fatalf("ParseSample: %v", err)
	}
	if s.SecondsIntoYear != 100 || s.Nano != 500 {
		t.Errorf("secs/nano = %d/%d", s.SecondsIntoYear, s.Nano)
	}
	v, ok := s.Val.(float64)
	if !ok || v != 3.14 {
		t.Errorf("Val = %v, want 3.14", s.Val)
	}
}

func TestUnescape(t *testing.T) {
	in := []byte{0x1b, 0x01, 'a', 0x1b, 0x02, 'b', 0x1b, 0x03}
	got := unescape(in)
	want := []byte{0x1b, 'a', 0x0a, 'b', 0x0d}
	if !bytes.Equal(got, want) {
		t.Errorf("unescape() = %v, want %v", got, want)
	}
}

func TestUnpackRawData(t *testing.T) {
	var header buf
	header.varint(1, uint64(ScalarDouble))
	header.bytesField(2, []byte("TEST:pv"))
	header.varint(3, 1970)

	var s1 buf
	s1.varint(1, 0)
	s1.varint(2, 0)
	s1.fixed64(3, math.Float64bits(1.5))

	var s2 buf
	s2.varint(1, 1)
	s2.varint(2, 0)
	s2.fixed64(3, math.Float64bits(2.5))

	data := bytes.Join([][]byte{header.b.Bytes(), s1.b.Bytes(), s2.b.Bytes()}, []byte("\n"))

	pvData, err := UnpackRawData(data)
	if err != nil {
		t.Fatalf("UnpackRawData: %v", err)
	}
	if pvData.Info.PVName != "TEST:pv" {
		t.Errorf("PVName = %q", pvData.Info.PVName)
	}
	if len(pvData.Samples) != 2 {
		t.Fatalf("len(Samples) = %d, want 2", len(pvData.Samples))
	}
	if pvData.Samples[0].Val.(float64) != 1.5 {
		t.Errorf("Samples[0].Val = %v, want 1.5", pvData.Samples[0].Val)
	}
	if pvData.Samples[1].Val.(float64) != 2.5 {
		t.Errorf("Samples[1].Val = %v, want 2.5", pvData.Samples[1].Val)
	}
}
