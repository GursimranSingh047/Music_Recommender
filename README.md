MoodTune — Emotion-Aware Personalized Music Recommendation System ( Currently upgrading old project)

                   Final Architecture
                    ┌─────────────────────┐
                    │       USER          │
                    └──────────┬──────────┘
                               │
                     Webcam / Manual Mood
                               │
                               ▼
                 ┌─────────────────────────┐
                 │ Facial Emotion Detection│
                 │       ML Model          │
                 └────────────┬────────────┘
                              │
                       Emotion + Confidence
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Recommendation Engine   │
                 │                         │
                 │ Emotion                 │
                 │ Genre                   │
                 │ Language                │
                 │ User Preferences        │
                 │ Feedback                │
                 └────────────┬────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Music API     │
                    └────────┬─────────┘
                             │
                             ▼
                    Personalized Songs
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
              Like/Dislike          History
