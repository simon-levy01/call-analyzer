# Conversation Copilot

A private assistive application that helps an autistic user interpret and respond during a selected one-to-one conversation while preserving long-term, contact-specific context.

## Language

**Conversation Copilot**:
The application that provides cautious, contact-aware guidance during conversations chosen by the user.
_Avoid_: Autistic Analyzer, emotion detector, people reader

**Assisted Call**:
A one-to-one video or voice conversation that the user has explicitly selected for live support.
_Avoid_: recording session, monitored call

**Selected Call Window**:
The visible WhatsApp Desktop, Zoom, or dedicated Google Chrome window with an active Google Meet call that the user explicitly chooses as the source for an Assisted Call.
_Avoid_: desktop recording, hidden capture, automatic window target

**Selected Contact**:
The person whom the user confirms as the other participant before contact memory is used or changed.
_Avoid_: detected person, target, subject

**Contact Suggestion**:
A proposed match derived from visible window text, saved aliases, or conversation context that the user must confirm or replace.
_Avoid_: automatic identity, facial recognition

**Contact Alias**:
A platform name or other identifier linked to one selected contact with the user's confirmation.
_Avoid_: username identity, biometric match

**Conversation Turn**:
A bounded spoken or written contribution attributed either to the user or the selected contact.
_Avoid_: audio chunk, message blob

**Speaker Role**:
The attribution of a Conversation Turn to the user, the selected contact, or unclear when attribution is not reliable.
_Avoid_: detected speaker identity, assumed sender

**Remote Face Region**:
The single visible area believed to contain the selected contact's face, normally initialized from the largest face in the Selected Call Window and correctable by the user. Other visible faces, including the user's self-preview, are not analysis subjects.
_Avoid_: face identity, biometric profile

**Remote Face Selection**:
The user's temporary choice of which visible face belongs to the other participant in the current Assisted Call. It assigns an analysis role only and does not name, recognize, or remember a person.
_Avoid_: facial identity, biometric recognition, remembered face

**Facial Signal**:
A local, time-bounded measurement of visible geometry or movement from the Remote Face Region before any interpretation.
_Avoid_: detected emotion, facial truth, self-analysis

**Observation**:
A time-bounded piece of visible, vocal, or linguistic information produced during an assisted call before interpretation.
_Avoid_: emotion, conclusion

**Tone Hypothesis**:
A cautious possible description of the current affective tone, such as happy, sad, angry or tense, emotionally intense, neutral, or unclear.
_Avoid_: detected emotion, emotional truth

**Social Cue**:
A possible conversational meaning or change in engagement supported by current observations and context.
_Avoid_: intent, diagnosis, proof

**Evidence**:
The observable words, vocal behavior, facial movement, or remembered context that influenced a tone hypothesis or social cue.
_Avoid_: certainty, proof

**Confidence Level**:
The qualitative strength of support for an interpretation: low, medium, high, or unclear.
_Avoid_: certainty percentage, probability

**Live Guidance**:
The limited set of current tone hypotheses, cues, replies, reminders, and follow-up questions offered during an assisted call.
_Avoid_: dashboard feed, instruction

**Conversation Memory**:
Long-lived, locally stored context associated with a selected contact and available across imported text and assisted calls.
_Avoid_: transcript archive, cloud profile

**Memory Proposal**:
A candidate addition, correction, supersession, or removal that requires user review before changing conversation memory.
_Avoid_: automatic memory, inferred fact

**Approved Memory**:
A memory proposal accepted or edited by the user and retained until corrected, superseded, or deleted by the user.
_Avoid_: model belief, permanent truth

**Superseded Memory**:
An approved memory kept as history but excluded from current guidance because newer approved information replaced it.
_Avoid_: deleted memory, current fact

**Interaction Style**:
The reviewed pattern of how the user and a particular contact communicate with each other, used to tailor suggestions for that relationship.
_Avoid_: user personality, global writing style

**Feature Plan**:
The implementation agreement for one feature, created immediately before that feature begins and bounded by the master plan.
_Avoid_: master roadmap, speculative design

**Feature Column**:
The permanent Trello column containing the planning, implementation, validation, review, and correction work for one feature.
_Avoid_: temporary status column, sprint

**Claude Review Gate**:
The required independent QA and code-review handoff that a code feature must pass before completion.
_Avoid_: optional review, final polish
