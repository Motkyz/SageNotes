package ru.sagenotes.ocrservice.model;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "notes")
public class NoteModel {

    @Getter
    @Id
    private UUID id;

    @Getter
    @Column(name = "owner_id")
    private UUID ownerId;

    @Setter
    @Getter
    @OneToMany(mappedBy = "note", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    private List<OCRModel> ocrs = new ArrayList<>();

    public void addOCR(OCRModel ocr) {
        ocrs.removeIf(x -> x.getFid().equals(ocr.getFid()));
        this.ocrs.add(ocr);
        ocr.setNote(this);
    }

    public void removeOCR(OCRModel ocr) {
        this.ocrs.remove(ocr);
        ocr.setNote(null);
    }
}
