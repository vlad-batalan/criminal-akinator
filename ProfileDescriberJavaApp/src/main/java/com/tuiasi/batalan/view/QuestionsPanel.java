package com.tuiasi.batalan.view;

import com.tuiasi.batalan.model.data.QuestionAnswerModel;
import com.tuiasi.batalan.model.data.QuestionModel;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionListener;
import java.util.HashMap;
import java.util.Map;

public class QuestionsPanel extends JPanel {
    private final JButton filterQuestionsButton;
    private final JTextField filterQuestionsTextField;
    private final JPanel questionsPanel;
    private final Map<String, QuestionAnswerPanel> questionComponents;

    public QuestionsPanel() {
        super();
        this.setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));

        // Header component with static instructions and filter bar.
        JPanel questionsHeaderPanel = new JPanel();
        questionsHeaderPanel.setLayout(new GridLayout(2, 1));

        // Instructions label.
        JLabel instructionsLabel = new JLabel("<html>" +
                                              "<p>If both Yes/No questions fit for a query, </p>" +
                                              "<p>then check both answers.</p>" +
                                              "</html>", SwingConstants.CENTER);
        // Filter text field.
        this.filterQuestionsTextField = new JTextField(10);
        this.filterQuestionsTextField.setMaximumSize(new Dimension(Integer.MAX_VALUE,
                this.filterQuestionsTextField.getPreferredSize().height));

        // Button to filter the questions.
        this.filterQuestionsButton = new JButton("Filter questions");

        // Both button and text field are organized within a single JPanel component.
        JPanel filterPanel = new JPanel();
        filterPanel.add(this.filterQuestionsTextField);
        filterPanel.add(this.filterQuestionsButton);

        // Add all to header panel.
        questionsHeaderPanel.add(instructionsLabel);
        questionsHeaderPanel.add(filterPanel);

        // Scrollable questions component.
        JScrollPane formScrollPane = new JScrollPane(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
                JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
        formScrollPane.getVerticalScrollBar().setUnitIncrement(20);
        formScrollPane.getViewport().setScrollMode(JViewport.BACKINGSTORE_SCROLL_MODE);

        // Create component with questions.
        this.questionsPanel = new JPanel();
        this.questionsPanel.setLayout(new GridLayout(0, 1, 3, 3));
        this.questionsPanel.setBackground(Color.LIGHT_GRAY);

        this.questionComponents = new HashMap<>();

        // Add component to scrollable area.
        formScrollPane.add(questionsPanel);
        formScrollPane.setViewportView(questionsPanel);

        this.add(questionsHeaderPanel);
        this.add(formScrollPane);

        this.setVisible(true);
    }

    public void updateQuestions(QuestionAnswerModel model) {
        // Update question components.
        // - reset questions.
        this.questionsPanel.removeAll();

        // Sync with component map
        for (QuestionModel question: model.getQuestionMap().values()) {
            // Add a new component if it doesn't exist.
            if (!this.questionComponents.containsKey(question.getName())) {
                QuestionAnswerPanel questionAnswerPanel = new QuestionAnswerPanel();
                questionAnswerPanel.setQuestion(question);
                this.questionComponents.put(question.getName(), questionAnswerPanel);
            }

            // Get the component.
            QuestionAnswerPanel storedQuestion = this.questionComponents.get(question.getName());

            // Change the state.
            storedQuestion.setQuestion(question);

            // Add to canvas if is visible.
            if (question.isVisible()) {
                this.questionsPanel.add(storedQuestion);
            }
        }

        // If there are no components, add a default label component.
        if (this.questionsPanel.getComponents().length == 0) {
            this.questionsPanel.add(new JLabel("There are no questions selected."), SwingConstants.CENTER);
        }

        // Repaint.
        this.validate();
    }

    public Map<String, QuestionModel> getQuestions() {
        Map<String, QuestionModel> resultMap = new HashMap<>();

        for(Map.Entry<String, QuestionAnswerPanel> questionPanelEntry: this.questionComponents.entrySet()) {
            QuestionModel questionModel = QuestionModel.builder()
                    .withName(questionPanelEntry.getKey())
                    .withAnswers(questionPanelEntry.getValue().getAnswers())
                    .build();

            resultMap.put(questionPanelEntry.getKey(), questionModel);
        }

        return resultMap;
    }

    public String getFilterQuery() {
        return this.filterQuestionsTextField.getText();
    }

    public void onFilterQuestionsClick(ActionListener e) {
        this.filterQuestionsButton.addActionListener(e);
    }
}
