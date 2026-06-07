package ru.sagenotes.ocrservice.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class OCRRequestListDTO {

    @NotNull
    private String noteId;

    @Valid
    private List<OCRRequestDTO> files;
}
