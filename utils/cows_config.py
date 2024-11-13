"""COWS (Clinical Opiate Withdrawal Scale) configuration"""

COWS_TOOL = {
    "name": "Clinical Opiate Withdrawal Scale (COWS)",
    "description": "The Clinical Opiate Withdrawal Scale (COWS) is a clinical assessment tool used to measure the severity of opiate withdrawal symptoms.",
    "version": "1.0",
    "tool_type": "COWS",
    "scoring_logic": {
        "ranges": [
            {"min": 0, "max": 4, "severity": "Mild", "description": "Mild withdrawal"},
            {"min": 5, "max": 12, "severity": "Moderate", "description": "Moderate withdrawal"},
            {"min": 13, "max": 24, "severity": "Moderately severe", "description": "Moderately severe withdrawal"},
            {"min": 25, "max": 36, "severity": "Severe", "description": "Severe withdrawal"}
        ],
        "max_score": 36
    },
    "questions": [
        {
            "question_text": "Resting Pulse Rate (beats/minute)",
            "order": 1,
            "question_type": "scale",
            "required": True,
            "help_text": "Measure after patient is sitting/lying for one minute",
            "options": [
                {"text": "Pulse 80 or below", "value": "0", "score": 0},
                {"text": "Pulse 81-100", "value": "1", "score": 1},
                {"text": "Pulse 101-120", "value": "2", "score": 2},
                {"text": "Pulse greater than 120", "value": "4", "score": 4}
            ]
        },
        {
            "question_text": "Sweating",
            "order": 2,
            "question_type": "scale",
            "required": True,
            "help_text": "Over past 30 minutes not accounted for by room temperature or patient activity",
            "options": [
                {"text": "No report of chills or flushing", "value": "0", "score": 0},
                {"text": "Subjective report of chills or flushing", "value": "1", "score": 1},
                {"text": "Flushed or observable moistness on face", "value": "2", "score": 2},
                {"text": "Beads of sweat on brow or face", "value": "3", "score": 3},
                {"text": "Sweat streaming off face", "value": "4", "score": 4}
            ]
        },
        {
            "question_text": "Restlessness",
            "order": 3,
            "question_type": "scale",
            "required": True,
            "help_text": "Observation during assessment",
            "options": [
                {"text": "Able to sit still", "value": "0", "score": 0},
                {"text": "Reports difficulty sitting still, but is able to do so", "value": "1", "score": 1},
                {"text": "Frequent shifting or extraneous movements of legs/arms", "value": "3", "score": 3},
                {"text": "Unable to sit still for more than a few seconds", "value": "5", "score": 5}
            ]
        },
        {
            "question_text": "Pupil size",
            "order": 4,
            "question_type": "scale",
            "required": True,
            "help_text": "Observe in normal room light",
            "options": [
                {"text": "Pupils pinned or normal size for room light", "value": "0", "score": 0},
                {"text": "Pupils possibly larger than normal for room light", "value": "1", "score": 1},
                {"text": "Pupils moderately dilated", "value": "2", "score": 2},
                {"text": "Pupils so dilated that only rim of iris is visible", "value": "5", "score": 5}
            ]
        },
        {
            "question_text": "Bone or Joint aches",
            "order": 5,
            "question_type": "scale",
            "required": True,
            "help_text": "If patient was having pain previously, only the additional component attributed to opiates withdrawal is scored",
            "options": [
                {"text": "Not present", "value": "0", "score": 0},
                {"text": "Mild diffuse discomfort", "value": "1", "score": 1},
                {"text": "Patient reports severe diffuse aching of joints/muscles", "value": "2", "score": 2},
                {"text": "Patient is rubbing joints or muscles and is unable to sit still because of discomfort", "value": "4", "score": 4}
            ]
        },
        {
            "question_text": "Runny nose or tearing",
            "order": 6,
            "question_type": "scale",
            "required": True,
            "help_text": "Not accounted for by cold symptoms or allergies",
            "options": [
                {"text": "Not present", "value": "0", "score": 0},
                {"text": "Nasal stuffiness or unusually moist eyes", "value": "1", "score": 1},
                {"text": "Nose running or tearing", "value": "2", "score": 2},
                {"text": "Nose constantly running or tears streaming down cheeks", "value": "4", "score": 4}
            ]
        },
        {
            "question_text": "GI Upset",
            "order": 7,
            "question_type": "scale",
            "required": True,
            "help_text": "Over last 30 minutes",
            "options": [
                {"text": "No GI symptoms", "value": "0", "score": 0},
                {"text": "Stomach cramps", "value": "1", "score": 1},
                {"text": "Nausea or loose stool", "value": "2", "score": 2},
                {"text": "Vomiting or diarrhea", "value": "3", "score": 3},
                {"text": "Multiple episodes of vomiting or diarrhea", "value": "5", "score": 5}
            ]
        },
        {
            "question_text": "Tremor",
            "order": 8,
            "question_type": "scale",
            "required": True,
            "help_text": "Observation of outstretched hands",
            "options": [
                {"text": "No tremor", "value": "0", "score": 0},
                {"text": "Tremor can be felt, but not observed", "value": "1", "score": 1},
                {"text": "Slight tremor observable", "value": "2", "score": 2},
                {"text": "Gross tremor or muscle twitching", "value": "4", "score": 4}
            ]
        },
        {
            "question_text": "Yawning",
            "order": 9,
            "question_type": "scale",
            "required": True,
            "help_text": "Observation during assessment",
            "options": [
                {"text": "No yawning", "value": "0", "score": 0},
                {"text": "Yawning once or twice during assessment", "value": "1", "score": 1},
                {"text": "Yawning three or more times during assessment", "value": "2", "score": 2},
                {"text": "Yawning several times/minute", "value": "4", "score": 4}
            ]
        },
        {
            "question_text": "Anxiety or Irritability",
            "order": 10,
            "question_type": "scale",
            "required": True,
            "help_text": "Observation during assessment",
            "options": [
                {"text": "None", "value": "0", "score": 0},
                {"text": "Patient reports increasing irritability or anxiousness", "value": "1", "score": 1},
                {"text": "Patient obviously irritable or anxious", "value": "2", "score": 2},
                {"text": "Patient so irritable or anxious that participation in the assessment is difficult", "value": "4", "score": 4}
            ]
        },
        {
            "question_text": "Gooseflesh skin",
            "order": 11,
            "question_type": "scale",
            "required": True,
            "help_text": "Can be felt or observed in a room of adequate temperature",
            "options": [
                {"text": "Skin is smooth", "value": "0", "score": 0},
                {"text": "Piloerrection of skin can be felt or hairs standing up on arms", "value": "3", "score": 3},
                {"text": "Prominent piloerrection", "value": "5", "score": 5}
            ]
        }
    ]
}
