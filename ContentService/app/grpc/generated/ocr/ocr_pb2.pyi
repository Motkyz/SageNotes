from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OcrByNoteRequest(_message.Message):
    __slots__ = ("note_id",)
    NOTE_ID_FIELD_NUMBER: _ClassVar[int]
    note_id: str
    def __init__(self, note_id: _Optional[str] = ...) -> None: ...

class OcrFileRequest(_message.Message):
    __slots__ = ("fid", "file_url")
    FID_FIELD_NUMBER: _ClassVar[int]
    FILE_URL_FIELD_NUMBER: _ClassVar[int]
    fid: str
    file_url: str
    def __init__(self, fid: _Optional[str] = ..., file_url: _Optional[str] = ...) -> None: ...

class ProcessOcrRequest(_message.Message):
    __slots__ = ("note_id", "files")
    NOTE_ID_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    note_id: str
    files: _containers.RepeatedCompositeFieldContainer[OcrFileRequest]
    def __init__(self, note_id: _Optional[str] = ..., files: _Optional[_Iterable[_Union[OcrFileRequest, _Mapping]]] = ...) -> None: ...

class OcrFileResponse(_message.Message):
    __slots__ = ("fid", "text")
    FID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    fid: str
    text: str
    def __init__(self, fid: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class OcrResponseList(_message.Message):
    __slots__ = ("note_id", "files")
    NOTE_ID_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    note_id: str
    files: _containers.RepeatedCompositeFieldContainer[OcrFileResponse]
    def __init__(self, note_id: _Optional[str] = ..., files: _Optional[_Iterable[_Union[OcrFileResponse, _Mapping]]] = ...) -> None: ...
