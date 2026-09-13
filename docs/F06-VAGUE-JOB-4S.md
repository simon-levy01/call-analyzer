# Vague lost-job transcript: four-second concurrent feed

Current production retrieval, coordinator and Terra-low guidance. Ten turns arrived every four seconds while API requests ran in a worker thread. Model cadence remained twelve seconds. No physical audio or Tk UI capture. All memories were fictional and approved before this call.

## Transcript and feed timing

| Planned | Actual | Speaker | Words |
|---|---|---|---|
| 0s | 0.000s | user | How have you been? |
| 4s | 4.015s | selected_contact | I feel stressed. |
| 8s | 8.015s | user | What has been on your mind? |
| 12s | 12.000s | selected_contact | I do not know how I am going to pay rent. |
| 16s | 16.000s | user | That sounds like a lot to deal with. |
| 20s | 20.015s | selected_contact | I was there for so long. It was such a big part of my life. |
| 24s | 24.000s | user | I am listening. |
| 28s | 28.000s | selected_contact | Now I am not sure what the future holds. I do not know what comes next. |
| 32s | 32.000s | user | Okay, we can talk about something else. |
| 36s | 36.000s | selected_contact | Changing the subject: I am enjoying a new mystery novel. |

Maximum feed timing error: 0.015s. No waiting for a model response before delivering the next turn.

## Expected behavior

Stress alone does not establish job loss. Rent worries combined with remembered layoff/rent concerns can surface that memory as a possibility. Long tenure and uncertainty add context without establishing the employer or cause of departure. Irrelevant exam/cafe memories should not become model-selected reminders. Replies should offer support rather than assert a firing or ask which remembered event this is.

## Observed behavior

- At 4s, stress retrieved an exam candidate internally; it was not dispatched or selected as a reminder at that point.
- At 12s, rent wording retrieved the McDonald's layoff memory alongside exam and former-cafe-job distractors. The stored layoff memory explicitly mentions rent, so lexical overlap helped; this is not evidence of a purely semantic match to a memory containing no rent detail.
- First request started at 12.109s using turns 1-4. At 20.047s, Terra selected only the layoff memory as “Possibly related.” It had not seen the later long-tenure/future wording in that request.
- The first raw reply was “I’m sorry—you’re dealing with a lot. Do you want to talk through what options you have?” New speech had arrived by then, so current application rules cleared all ready replies/follow-ups while retaining analysis and the reminder. This is an observed remaining responsiveness limitation, not a displayed reply success.
- The 24.156s request used turns through 7, where the user spoke last. It returned analysis but no new reminder or reply at 29.203s. Later future-uncertainty speech arrived at 28s and remained a retrieval match, but was not separately sent before the next scheduled request.
- The 36s explicit book-topic change removed memory candidates. The final model output arrived at approximately 44.25s with no selected memory. Existing UI retention was not exercised in this harness, so no exact disappearance time is claimed.

## Actual responses

### Request through turn 4: 12.109s → 20.047s

**Selected context:** Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.

**Raw model output:**
```json
{
  "status": "updated",
  "tones": [
    {
      "kind": "tense_negative",
      "confidence": "medium",
      "hypothesis": "The contact explicitly describes feeling stressed and worries about being able to pay rent.",
      "evidence": {
        "explanation": "They say, “I feel stressed” and “I do not know how I am going to pay rent.”",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "social_cues": [
    {
      "kind": "uncertainty",
      "confidence": "medium",
      "hypothesis": "The contact explicitly expresses uncertainty about how to cover rent.",
      "evidence": {
        "explanation": "They say, “I do not know how I am going to pay rent.”",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "explanation": null,
  "replies": [
    {
      "text": "I’m sorry—you’re dealing with a lot. Do you want to talk through what options you have?",
      "confidence": "high",
      "turn_ids": [
        4
      ],
      "memory_ids": [],
      "preference_ids": []
    },
    {
      "text": "That sounds really stressful. Is there anything I can do to help you think it through?",
      "confidence": "high",
      "turn_ids": [
        2,
        4
      ],
      "memory_ids": [],
      "preference_ids": []
    },
    {
      "text": "I’m sorry. Have you been able to look into any help with rent yet?",
      "confidence": "medium",
      "turn_ids": [
        4
      ],
      "memory_ids": [],
      "preference_ids": []
    }
  ],
  "remember": [
    {
      "text": "Possibly related: Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.",
      "confidence": "medium",
      "turn_ids": [
        4
      ],
      "memory_ids": [
        "157fcc9c-3943-4a31-b7b6-b0ba8a68c630"
      ],
      "preference_ids": []
    }
  ],
  "follow_up": [
    {
      "text": "Have you been able to find out whether there’s any rent assistance available?",
      "confidence": "medium",
      "turn_ids": [
        4
      ],
      "memory_ids": [],
      "preference_ids": []
    },
    {
      "text": "Do you want to make a plan for what to do next?",
      "confidence": "high",
      "turn_ids": [
        4
      ],
      "memory_ids": [],
      "preference_ids": []
    }
  ],
  "snapshot_id": 4,
  "generation": 1,
  "manual": false
}
```

**Delivered output after newer-speech filtering:**
```json
{
  "status": "updated",
  "tones": [
    {
      "kind": "tense_negative",
      "confidence": "medium",
      "hypothesis": "The contact explicitly describes feeling stressed and worries about being able to pay rent.",
      "evidence": {
        "explanation": "They say, “I feel stressed” and “I do not know how I am going to pay rent.”",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "social_cues": [
    {
      "kind": "uncertainty",
      "confidence": "medium",
      "hypothesis": "The contact explicitly expresses uncertainty about how to cover rent.",
      "evidence": {
        "explanation": "They say, “I do not know how I am going to pay rent.”",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "explanation": null,
  "replies": [],
  "remember": [
    {
      "text": "Possibly related: Maya was laid off from her job at McDonald's on September 1, 2026, and is worried about paying rent.",
      "confidence": "medium",
      "turn_ids": [
        4
      ],
      "memory_ids": [
        "157fcc9c-3943-4a31-b7b6-b0ba8a68c630"
      ],
      "preference_ids": []
    }
  ],
  "follow_up": [],
  "snapshot_id": 4,
  "generation": 1,
  "manual": false
}
```

### Request through turn 7: 24.156s → 29.203s

**Selected context:** None

**Raw model output:**
```json
{
  "status": "updated",
  "tones": [
    {
      "kind": "tense_negative",
      "confidence": "medium",
      "hypothesis": "The contact explicitly says they feel stressed.",
      "evidence": {
        "explanation": "They say, “I feel stressed,” while describing uncertainty about paying rent.",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "social_cues": [
    {
      "kind": "uncertainty",
      "confidence": "medium",
      "hypothesis": "The contact expresses uncertainty about meeting rent payments.",
      "evidence": {
        "explanation": "They say, “I do not know how I am going to pay rent.”",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "explanation": null,
  "replies": [],
  "remember": [],
  "follow_up": [],
  "snapshot_id": 7,
  "generation": 1,
  "manual": false
}
```

**Delivered output after newer-speech filtering:**
```json
{
  "status": "updated",
  "tones": [
    {
      "kind": "tense_negative",
      "confidence": "medium",
      "hypothesis": "The contact explicitly says they feel stressed.",
      "evidence": {
        "explanation": "They say, “I feel stressed,” while describing uncertainty about paying rent.",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "social_cues": [
    {
      "kind": "uncertainty",
      "confidence": "medium",
      "hypothesis": "The contact expresses uncertainty about meeting rent payments.",
      "evidence": {
        "explanation": "They say, “I do not know how I am going to pay rent.”",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "explanation": null,
  "replies": [],
  "remember": [],
  "follow_up": [],
  "snapshot_id": 7,
  "generation": 1,
  "manual": false
}
```

### Request through turn 10: 36.156s → 44.250s

**Selected context:** None

**Raw model output:**
```json
{
  "status": "updated",
  "tones": [
    {
      "kind": "tense_negative",
      "confidence": "medium",
      "hypothesis": "The contact explicitly described feeling stressed about paying rent and uncertainty about the future.",
      "evidence": {
        "explanation": "They said “I feel stressed” and expressed not knowing how they would pay rent or what comes next.",
        "modalities": [
          "language"
        ]
      }
    },
    {
      "kind": "positive_warm",
      "confidence": "medium",
      "hypothesis": "The contact may be shifting to a more positive topic while discussing a novel they are enjoying.",
      "evidence": {
        "explanation": "They said they are enjoying a new mystery novel.",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "social_cues": [
    {
      "kind": "uncertainty",
      "confidence": "high",
      "hypothesis": "The contact explicitly conveyed uncertainty about what comes next.",
      "evidence": {
        "explanation": "They said they were not sure what the future holds and did not know what comes next.",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "explanation": null,
  "replies": [
    {
      "text": "What mystery novel are you reading?",
      "confidence": "high",
      "turn_ids": [
        10
      ],
      "memory_ids": [],
      "preference_ids": []
    },
    {
      "text": "What are you enjoying about it so far?",
      "confidence": "high",
      "turn_ids": [
        10
      ],
      "memory_ids": [],
      "preference_ids": []
    }
  ],
  "remember": [],
  "follow_up": [],
  "snapshot_id": 10,
  "generation": 1,
  "manual": false
}
```

**Delivered output after newer-speech filtering:**
```json
{
  "status": "updated",
  "tones": [
    {
      "kind": "tense_negative",
      "confidence": "medium",
      "hypothesis": "The contact explicitly described feeling stressed about paying rent and uncertainty about the future.",
      "evidence": {
        "explanation": "They said “I feel stressed” and expressed not knowing how they would pay rent or what comes next.",
        "modalities": [
          "language"
        ]
      }
    },
    {
      "kind": "positive_warm",
      "confidence": "medium",
      "hypothesis": "The contact may be shifting to a more positive topic while discussing a novel they are enjoying.",
      "evidence": {
        "explanation": "They said they are enjoying a new mystery novel.",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "social_cues": [
    {
      "kind": "uncertainty",
      "confidence": "high",
      "hypothesis": "The contact explicitly conveyed uncertainty about what comes next.",
      "evidence": {
        "explanation": "They said they were not sure what the future holds and did not know what comes next.",
        "modalities": [
          "language"
        ]
      }
    }
  ],
  "explanation": null,
  "replies": [
    {
      "text": "What mystery novel are you reading?",
      "confidence": "high",
      "turn_ids": [
        10
      ],
      "memory_ids": [],
      "preference_ids": []
    },
    {
      "text": "What are you enjoying about it so far?",
      "confidence": "high",
      "turn_ids": [
        10
      ],
      "memory_ids": [],
      "preference_ids": []
    }
  ],
  "remember": [],
  "follow_up": [],
  "snapshot_id": 10,
  "generation": 1,
  "manual": false
}
```

## Cost and limits

Three real Terra-low requests cost **$0.0196996**. Aggregate recorded F06 evaluations: **$0.37665068**. No application changes were made in this test. Existing dated memories were reused; no new summary or memory extraction ran.

Raw timing, retrieval, model outputs, coordinator events and usage: `build/f06-lost-job-vague-4s.json`. Reproduce: `build/f06_lost_job_vague_4s.py`.
