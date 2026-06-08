package ru.sagenotes.searchservice.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SearchResult(
   @SerialName("note_id")
   val noteId: String,
   @SerialName("text")
   val text: String,
   @SerialName("score")
   val score: Double,
   @SerialName("source")
   val source: SearchSource
)