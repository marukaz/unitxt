from unitxt.blocks import Task
from unitxt.catalog import add_to_catalog

add_to_catalog(
    Task(
        inputs={"question": "str", "answer": "str", "reference_answer": "str"},
        outputs={"rating": "float"},
        metrics=["metrics.spearman"],
    ),
    "tasks.response_assessment.rating.single_turn_with_reference",
    overwrite=True,
)
