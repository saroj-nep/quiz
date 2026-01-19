

# ============================================================================
# IMPORTS - Load the libraries we need
# ============================================================================

import streamlit as st  # For creating the web interface
import pandas as pd  # For working with data in tables (DataFrames)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

# Configure how the Streamlit page looks and behaves
# This must be the FIRST Streamlit command in your script
st.set_page_config(
    page_title="Class Quiz",  # Text shown in browser tab
    page_icon="📝",  # Icon shown in browser tab
    layout="wide"
)


# ============================================================================
# FUNCTION DEFINITIONS
# ============================================================================

def load_questions():
    """
    Load questions from CSV file

    Returns:
        DataFrame: All questions from the CSV file

    Why a function?
    - Separates the "what" (loading data) from "when" (we'll use it later)
    - Makes code reusable - can call this multiple times
    - Easier to test and debug
    """
    df = pd.read_csv("quiz_questions.csv")
    return df


def generate_quiz(df, num_easy=4, num_medium=4, num_hard=4):
    """
    Generate quiz with specified distribution of difficulties

    Args:
        df: DataFrame containing all available questions
        num_easy: How many easy questions to include (default: 4)
        num_medium: How many medium questions to include (default: 4)
        num_hard: How many medium+ questions to include (default: 4)

    Returns:
        DataFrame: Selected and shuffled quiz questions

    How it works:
    1. Filter questions by difficulty level
    2. Randomly sample the requested number from each difficulty
    3. Combine all selected questions
    4. Shuffle them so they're not grouped by difficulty
    5. Add question numbers
    """

    # STEP 1: Filter and sample easy questions
    # df[df['difficulty'] == 'easy'] filters for only easy questions
    # .sample(n=X) randomly picks X questions from those

    easy = df[df['difficulty'] == 'easy'].sample(n=4)


    # STEP 2: Filter and sample medium questions
    # Same process as easy questions
    medium = df[df['difficulty'] == 'medium'].sample(n=4)

    # STEP 3: Filter and sample hard (medium+) questions
    # Same process, but filtering for 'medium+' difficulty
    hard = df[df['difficulty'] == 'medium+'].sample(n=4)

    # STEP 4: Combine all selected questions into one DataFrame
    # pd.concat() stacks DataFrames vertically
    # ignore_index=True creates new row numbers starting from 0
    quiz = pd.concat([easy, medium, hard])

    # STEP 5: Shuffle the questions randomly
    # .sample(frac=1) means sample 100% of the rows in random order
    # .reset_index(drop=True) resets row numbers after shuffling
    quiz = quiz.sample(frac=1)

    # STEP 6: Add question numbers (1, 2, 3, ...)
    # range(1, len(quiz) + 1) creates numbers from 1 to total_questions
    # We store this in a new column called 'question_num'
    quiz['question_num'] = range(1, len(quiz) + 1)

    return quiz


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# IMPORTANT CONCEPT: Session State in Streamlit
#
# Streamlit reruns the entire script every time a user interacts with it.
# This means variables get reset unless we store them in session_state.
#
# st.session_state is like a persistent dictionary that survives reruns.
# Think of it as the app's "memory" across interactions.
#
# We initialize these values ONCE when the app first loads.

# Check if 'quiz' exists in session state
# This will be False the first time the app runs
if 'quiz' not in st.session_state:
    # First run: Load questions and generate quiz
    df_questions = load_questions()

    # Generate the quiz with our desired distribution
    # We store it in session_state so it persists across button clicks
    st.session_state.quiz = generate_quiz(
        df_questions,
        num_easy=4,  # 4 easy questions
        num_medium=4,  # 4 medium questions
        num_hard=4  # 4 hard questions
    )

    # Initialize whether to show the answer (start with hidden)
    st.session_state.show_answer = False

    # Initialize which question we're currently showing (start at 0 = first question)
    # We use 0-based indexing because that's how DataFrames work
    st.session_state.current_question = 0

# ============================================================================
# USER INTERFACE - TITLE SECTION
# ============================================================================

# Display main title at top of page
st.title("Programming for EduTech - Quiz")

# Add a horizontal line for visual separation
st.markdown("---")

# ============================================================================
# USER INTERFACE - TOP CONTROL BUTTONS
# ============================================================================

# Layout Strategy: Using columns for side-by-side elements
#
# st.columns([2, 1, 1, 1]) creates 4 columns with relative widths:
# - Column 1: width = 2 (twice as wide as others)
# - Columns 2, 3, 4: width = 1 each
#
# This puts the question counter on the left, buttons on the right.

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

# COLUMN 1: Question counter
with col1:
    # Display which question we're on and total questions
    # We add 1 to current_question because it's 0-indexed (0, 1, 2...)
    # but we want to show users (1, 2, 3...)
    st.subheader(f"Question {st.session_state.current_question + 1} of {len(st.session_state.quiz)}")

# COLUMN 2: Shuffle button
with col2:
    # Create a button that shuffles questions
    # use_container_width=True makes button fill the column width
    if st.button("Shuffle Questions", use_container_width=True):
        # Get the current quiz from session state
        quiz = st.session_state.quiz

        # Shuffle it: .sample(frac=1) randomly reorders all rows
        quiz = quiz.sample(frac=1).reset_index(drop=True)

        # Renumber the questions 1, 2, 3... after shuffling
        quiz['question_num'] = range(1, len(quiz) + 1)

        # Save the shuffled quiz back to session state
        st.session_state.quiz = quiz

        # Reset to first question after shuffling
        st.session_state.current_question = 0

        # Hide answer when we shuffle
        st.session_state.show_answer = False

        # st.rerun() forces Streamlit to rerun the script
        # This updates the display with our changes
        st.rerun()

# COLUMN 3: Show Answer button
with col3:
    if st.button("Show Answer", use_container_width=True):
        # Set flag to True - will display answer below
        st.session_state.show_answer = True
        st.rerun()  # Refresh to show the answer

# COLUMN 4: Hide Answer button
with col4:
    if st.button("Hide Answer", use_container_width=True):
        # Set flag to False - will hide answer below
        st.session_state.show_answer = False
        st.rerun()  # Refresh to hide the answer

# Another horizontal divider
st.markdown("---")

# ============================================================================
# USER INTERFACE - NAVIGATION BUTTONS
# ============================================================================

# Navigation: Previous and Next buttons to move between questions
#
# Layout: [Previous] [empty space] [Next]
# The middle column is 3x wider to create space between buttons

col1, col2, col3 = st.columns([1, 3, 1])

# COLUMN 1: Previous button
with col1:
    # Create Previous button
    # disabled=True makes the button unclickable when condition is met
    # We disable when current_question == 0 (already at first question)
    if st.button(
            "Previous",
            use_container_width=True,
            disabled=(st.session_state.current_question == 0)
    ):
        # Move back one question (subtract 1 from index)
        st.session_state.current_question -= 1

        # Hide answer when changing questions
        st.session_state.show_answer = False

        st.rerun()  # Refresh to show the previous question

# COLUMN 3: Next button (column 2 is empty for spacing)
with col3:
    # Create Next button
    # Disable when we're at the last question
    # len(quiz) - 1 because quiz has length 12, but last index is 11
    if st.button(
            "Next",
            use_container_width=True,
            disabled=(st.session_state.current_question == len(st.session_state.quiz) - 1)
    ):
        # Move forward one question (add 1 to index)
        st.session_state.current_question += 1

        # Hide answer when changing questions
        st.session_state.show_answer = False

        st.rerun()  # Refresh to show the next question

# ============================================================================
# DISPLAY CURRENT QUESTION
# ============================================================================

# Accessing the current question data
#
# We need to:
# 1. Get the quiz DataFrame from session state
# 2. Get the current question index
# 3. Use .iloc[] to get that specific row

# Get the full quiz DataFrame
quiz = st.session_state.quiz

# Get the current question as a Series (single row from DataFrame)
# .iloc[] accesses by position (0 = first row, 1 = second row, etc.)
current = quiz.iloc[st.session_state.current_question]

# Now 'current' contains all the data for this question:
# current['question'] = the question text
# current['option_a'] = first answer choice
# current['correct_answer'] = the right answer (A, B, C, or D)
# etc.

# ============================================================================
# DISPLAY QUESTION AND OPTIONS
# ============================================================================

# Display the question text
# We use f-string to insert the question from our data
st.markdown(f"{current['question']}")

# Display the four answer options
# Each gets its own line
st.markdown(f"A. {current['option_a']}")
st.markdown(f"B. {current['option_b']}")
st.markdown(f"C. {current['option_c']}")
st.markdown(f"D. {current['option_d']}")

# ============================================================================
# CONDITIONAL DISPLAY - SHOW ANSWER
# ============================================================================

# Conditional rendering: Only show answer when flag is True
#
# This is controlled by the "Show Answer" and "Hide Answer" buttons above.
# When show_answer is True, we display the correct answer in a green box.

# Check if we should show the answer
if st.session_state.show_answer:
    # st.success() creates a green success message box
    # We use **bold** formatting with markdown
    st.success(f"**Correct Answer: {current['correct_answer']}**")

# ============================================================================
# FOOTER
# ============================================================================

# Final horizontal divider at bottom
st.markdown("---")

