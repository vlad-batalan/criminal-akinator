package com.tuiasi.batalan.model.data;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder(setterPrefix = "with")
@AllArgsConstructor
@NoArgsConstructor
public class QuestionModel {
    private String name;
    private String[] answers;
    private boolean isVisible;
}
