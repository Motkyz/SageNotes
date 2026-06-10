package ru.sagenotes.ocrservice.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.UUID;

@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "ocrs")
public class OCRModel {

    @Getter
    @Id
    private UUID fid;

    @Getter
    @Column(name = "text", columnDefinition = "TEXT")
    private String text;

    @Getter
    @Setter
    @ManyToOne
    @JoinColumn(name = "noteId")
    @JsonBackReference
    private NoteModel note;
}
