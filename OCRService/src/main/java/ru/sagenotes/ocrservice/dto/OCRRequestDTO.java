package ru.sagenotes.ocrservice.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class OCRRequestDTO {

    @NotNull
    private String fid;

    @NotNull
    private String fileUrl;
}
