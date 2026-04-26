# Adjacent-mandate scorecard

    Control metrics:
    {
  "accepted_count": 1,
  "effort_units": 20,
  "aoy": 0.05,
  "first_accepted_step": 7,
  "rework_rate": 1.0,
  "evidence_completeness": 0.714,
  "severe_false_positive_count": 1,
  "package_dependence": 0.0
}

    Treatment metrics:
    {
  "accepted_count": 5,
  "effort_units": 20,
  "aoy": 0.25,
  "first_accepted_step": 2,
  "rework_rate": 0.0,
  "evidence_completeness": 1.0,
  "severe_false_positive_count": 0,
  "package_dependence": 1.0
}

    Comparison:
    {
  "comparison": {
    "aoy_uplift": 4.0,
    "speed_uplift": 0.7142857142857143,
    "rework_reduction": 1.0,
    "evidence_completeness_uplift": 0.40056022408963593,
    "safety_regression": false,
    "package_dependence": 1.0
  },
  "thresholds": {
    "aoy_uplift": 0.35,
    "speed_uplift": 0.3,
    "rework_reduction": 0.4,
    "evidence_completeness_uplift": 0.2,
    "no_safety_regression": true,
    "package_dependence": 0.3
  },
  "passes": {
    "aoy_uplift": true,
    "speed_uplift": true,
    "rework_reduction": true,
    "evidence_completeness_uplift": true,
    "no_safety_regression": true,
    "package_dependence": true,
    "adjacent_mandate_proof": true
  }
}
