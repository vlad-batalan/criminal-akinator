package com.tuiasi.batalan.view;

import com.tuiasi.batalan.model.data.QuestionModel;

import javax.swing.JCheckBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingConstants;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import java.util.ArrayList;
import java.util.List;


public class QuestionAnswerPanel extends JPanel {
    private final JLabel questionLabel;
    private final JCheckBox yesCheckbox;
    private final JCheckBox noCheckbox;

    public QuestionAnswerPanel() {
        this.setLayout(new GridLayout(2, 1,5, 5));

        this.questionLabel = new JLabel("", SwingConstants.CENTER);
        this.yesCheckbox = new JCheckBox("Yes", false);
        this.noCheckbox = new JCheckBox("No", false);

        this.add(this.questionLabel);

        JPanel answerPanel = new JPanel(new FlowLayout());
        answerPanel.add(this.yesCheckbox);
        answerPanel.add(this.noCheckbox);

        this.add(answerPanel);
    }
    public void setQuestion(QuestionModel questionModel) {
        this.questionLabel.setText(questionModel.getName());

        // Put checks.
        this.yesCheckbox.setSelected(false);
        this.noCheckbox.setSelected(false);

        for (String answer: questionModel.getAnswers()) {
            if ("Yes".equals(answer)) {
                this.yesCheckbox.setSelected(true);
            }
            if ("No".equals(answer)) {
                this.noCheckbox.setSelected(true);
            }
        }
    }

    public String[] getAnswers() {
        List<String> result = new ArrayList<>();
        if (this.yesCheckbox.isSelected()) {
            result.add("Yes");
        }
        if (this.noCheckbox.isSelected()) {
            result.add("No");
        }
        return result.toArray(new String[0]);
    }



}
