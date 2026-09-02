# F05 live test script

Use fictional details and a consenting participant. Leave about 15 seconds after the
remote reply so the 12-second interpretation cadence can complete.

## Setup

1. Confirm the test contact before starting memory retrieval.
2. Add this normal, high-confidence Event / date memory:
   `Maya's dog Pepper died on August 18`.
3. The approved fictional replay is
   `conversation_copilot/assets/f04/basic-video-chat.mp4`. Its opening dialogue is
   the primary indirect-reference case.

## Calls to try

| Case | User wording | Remote wording | Expected result |
|---|---|---|---|
| Indirect event + tone | “How are you doing after the event last week?” | “A little better. I still don't want to name it out loud, but thanks for checking.” | The card says the words may refer to Pepper. If tone uses that link, evidence sources include conversation words and approved memory. |
| Pronoun-like follow-up | “How have you been after that?” | “I'm feeling better, but I still miss her a lot.” | Pepper appears as possible remembered context, without claiming certainty about current emotion. |
| Brief retrieval miss | After Pepper appears, add one unrelated short exchange, wait past 24 seconds, then add another if needed. | Any ordinary replies. | Pepper remains visible through the brief miss, then disappears once 24 seconds have elapsed since its last matching analysis. Changing/deleting the memory or contact still clears it immediately. |
| Distinct dated events | Add `Maya moved apartment on August 20`, then ask “How have you been since the event?” | “It has been difficult.” | Only the newer apartment event appears as cautious possible context. Name Pepper or August 18 explicitly to retrieve the older event. |
| Same-date competing events | Add two plausible events with the same date, then ask “How have you been since the event?” | “It has been difficult.” | Both events appear as possibilities; memory is withheld from cloud interpretation until clarified. |
| Wrong contact | Switch to a contact with no Pepper memory and repeat the event wording. | “I'm doing okay.” | Pepper never appears. Old guidance clears immediately. |
| Sensitive permission off | Mark Pepper sensitive and leave cloud permission off. | Repeat the indirect event exchange. | Pepper is not sent or shown as cloud-eligible interpretation context. |
| Sensitive permission on | Enable permission on that exact sensitive memory revision. | Repeat the exchange. | Pepper can appear again. Revoking permission removes it again. |
| Unrelated date word | “How is pottery class going?” | “I made a blue bowl today.” | Pepper does not appear. |
| No confirmed contact | Clear the contact and repeat the event wording. | “It has been difficult.” | No retrieval or extraction occurs. |

## Recommended live sequence for Yaheli and another contact

1. With Yaheli's consent, create a **fictional** normal Event / date memory such as
   `Yaheli's fictional dog Pepper died on August 18` and run the indirect-event case.
2. Switch to a different confirmed contact and repeat the same wording. Pepper must
   not appear, and the Yaheli card must clear immediately.
3. Return to Yaheli in a second call and try “How have you been after that?” The
   approved Yaheli memory may appear again as a possibility, proving persistence.
4. Stop the call, review several proposals together, correct one approved item, and
   delete at least two selected test memories while leaving one unselected item intact.

Keep the test facts fictional even though the participants and call are real. Do not
use a real tragedy, phone number, medical detail, or other sensitive fact for this gate.

## Management checks

1. Ctrl/Shift-select several pending proposals and approve them together.
2. Ctrl/Shift-select several pending proposals and reject them together.
3. Ctrl/Shift-select several approved memories and choose **Delete selected**.
4. Confirm every selected memory disappears, including corrected revisions and search
   results, while unselected memories remain.

Record the displayed context, evidence sources, contact, permission state, and whether
the result appeared after the cadence. Do not mark the manual gate passed if any
wrong-contact, deleted, rejected, superseded, or sensitive-without-permission memory
appears.
