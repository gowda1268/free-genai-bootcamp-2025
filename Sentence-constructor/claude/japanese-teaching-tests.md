# Japanese Teaching System Test Documentation

## 1. Sentence Complexity Test Cases

### 1.1 Simple Sentences
```xml
<test-cases>
    <case id="simple-1">
        <english>I eat bread.</english>
        <vocabulary>
            <word>
                <japanese>食べる</japanese>
                <romaji>taberu</romaji>
                <english>eat</english>
            </word>
            <word>
                <japanese>パン</japanese>
                <romaji>pan</romaji>
                <english>bread</english>
            </word>
        </vocabulary>
        <structure>[Subject] [Object] [Verb].</structure>
        <considerations>
            - Basic sentence with subject, object, and verb
            - Present tense form
            - Subject can be omitted in Japanese
        </considerations>
    </case>
    <case id="simple-2">
        <english>The book is red.</english>
        <vocabulary>
            <word>
                <japanese>本</japanese>
                <romaji>hon</romaji>
                <english>book</english>
            </word>
            <word>
                <japanese>赤い</japanese>
                <romaji>akai</romaji>
                <english>red</english>
            </word>
        </vocabulary>
        <structure>[Subject] [Adjective].</structure>
        <considerations>
            - Simple descriptor sentence
            - Uses i-adjective
            - No verb needed in Japanese
        </considerations>
    </case>
</test-cases>

### 1.2 Compound Sentences
```xml
<test-cases>
    <case id="compound-1">
        <english>I eat bread and drink water.</english>
        <vocabulary>
            <word>
                <japanese>食べる</japanese>
                <romaji>taberu</romaji>
                <english>eat</english>
            </word>
            <word>
                <japanese>パン</japanese>
                <romaji>pan</romaji>
                <english>bread</english>
            </word>
            <word>
                <japanese>飲む</japanese>
                <romaji>nomu</romaji>
                <english>drink</english>
            </word>
            <word>
                <japanese>水</japanese>
                <romaji>mizu</romaji>
                <english>water</english>
            </word>
        </vocabulary>
        <structure>[Subject] [Object1] [Verb1], [Object2] [Verb2].</structure>
        <considerations>
            - Compound sentence with two actions
            - Subject shared between clauses
            - Uses て form for connection
        </considerations>
    </case>
</test-cases>

### 1.3 Complex Sentences
```xml
<test-cases>
    <case id="complex-1">
        <english>Because it's hot, I drink water.</english>
        <vocabulary>
            <word>
                <japanese>暑い</japanese>
                <romaji>atsui</romaji>
                <english>hot</english>
            </word>
            <word>
                <japanese>飲む</japanese>
                <romaji>nomu</romaji>
                <english>drink</english>
            </word>
            <word>
                <japanese>水</japanese>
                <romaji>mizu</romaji>
                <english>water</english>
            </word>
        </vocabulary>
        <structure>[Reason] [Subject] [Object] [Verb].</structure>
        <considerations>
            - Cause and effect relationship
            - Uses から for "because"
            - Weather description
        </considerations>
    </case>
</test-cases>

## 2. Vocabulary Edge Cases

### 2.1 Multiple Meanings
```xml
<vocabulary-test>
    <word>
        <japanese>かかる</japanese>
        <romaji>kakaru</romaji>
        <meanings>
            <meaning>to take (time)</meaning>
            <meaning>to cost (money)</meaning>
            <meaning>to hang (on something)</meaning>
        </meanings>
        <test-sentences>
            <sentence>How long does it take?</sentence>
            <sentence>How much does it cost?</sentence>
            <sentence>The picture hangs on the wall.</sentence>
        </test-sentences>
    </word>
</vocabulary-test>

### 2.2 Transitive/Intransitive Pairs
```xml
<vocabulary-test>
    <pair>
        <transitive>
            <japanese>開ける</japanese>
            <romaji>akeru</romaji>
            <english>to open (something)</english>
        </transitive>
        <intransitive>
            <japanese>開く</japanese>
            <romaji>aku</romaji>
            <english>to open (by itself)</english>
        </intransitive>
        <test-sentences>
            <sentence>I open the door.</sentence>
            <sentence>The door opens.</sentence>
        </test-sentences>
    </pair>
</vocabulary-test>

## 3. State Transition Tests

### 3.1 Valid Transitions
```xml
<transition-test>
    <scenario id="setup-to-attempt">
        <initial-state>Setup</initial-state>
        <input>私はパンを食べます。</input>
        <expected-state>Attempt</expected-state>
        <validation>
            - Input contains Japanese text
            - No question marks
            - Contains vocabulary from setup
        </validation>
    </scenario>
    <scenario id="attempt-to-clues">
        <initial-state>Attempt</initial-state>
        <input>How do I use particles?</input>
        <expected-state>Clues</expected-state>
        <validation>
            - Input is a question
            - References grammar concept
            - Related to previous attempt
        </validation>
    </scenario>
</transition-test>

### 3.2 Invalid Transitions
```xml
<transition-test>
    <scenario id="invalid-clues-to-setup">
        <initial-state>Clues</initial-state>
        <input>Can you give me the answer?</input>
        <expected-response>
            - Reminder that answers aren't provided
            - Offer additional clues
            - Encourage attempt
        </expected-response>
    </scenario>
</transition-test>

## 4. Teaching Scenario Tests

### 4.1 Common Mistakes
```xml
<teaching-test>
    <scenario id="particle-mistake">
        <student-attempt>私が学校に行きます。</student-attempt>
        <error>Incorrect use of が particle for regular actions</error>
        <expected-guidance>
            - Acknowledge attempt
            - Explain は vs が without giving answer
            - Encourage new attempt
        </expected-guidance>
    </scenario>
    <scenario id="conjugation-mistake">
        <student-attempt>私は食べりました。</student-attempt>
        <error>Incorrect る verb conjugation</error>
        <expected-guidance>
            - Point out verb type (る verb)
            - Review past tense formation rules
            - Encourage correction
        </expected-guidance>
    </scenario>
</teaching-test>

## 5. Validation Criteria

### 5.1 Response Scoring
```xml
<scoring-criteria>
    <category name="vocabulary-table">
        <criteria>
            - Contains all necessary words (2 points)
            - Correct formatting (2 points)
            - Dictionary forms only (2 points)
            - No particle inclusion (2 points)
            - Appropriate difficulty level (2 points)
        </criteria>
    </category>
    <category name="sentence-structure">
        <criteria>
            - Clear bracketed format (2 points)
            - No conjugations shown (2 points)
            - Appropriate for level (2 points)
            - Matches example patterns (2 points)
            - No particles included (2 points)
        </criteria>
    </category>
</scoring-criteria>

## 6. Documentation Improvements

### 6.1 Version Control
```xml
<version-control>
    <version number="1.0">
        <changes>
            - Initial test documentation
            - Basic test cases added
            - State transition examples
        </changes>
        <date>2025-01-03</date>
    </version>
    <planned-improvements>
        - Add more complex sentence patterns
        - Expand vocabulary edge cases
        - Include cultural context tests
        - Add error recovery scenarios
    </planned-improvements>
</version-control>

### 6.2 Cross-References
```xml
<cross-references>
    <reference id="particles">
        <related-sections>
            - Vocabulary Table Guidelines
            - Common Mistakes
            - Teaching Scenarios
        </related-sections>
        <purpose>Ensure consistent particle handling across documentation</purpose>
    </reference>
    <reference id="verb-conjugation">
        <related-sections>
            - Sentence Structure Guidelines
            - Teaching Scenarios
            - Validation Criteria
        </related-sections>
        <purpose>Maintain consistent verb form handling</purpose>
    </reference>
</cross-references>