package com.tuiasi.batalan.model.data;

import com.tuiasi.batalan.model.data.QuestionModel;
import lombok.Builder;
import lombok.Data;

import java.util.Map;

@Data
@Builder(setterPrefix = "with")
public class QuestionAnswerModel {
    private Map<String, QuestionModel> questionMap;
}
