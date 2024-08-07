from unitxt import add_to_catalog
from unitxt.blocks import LoadHF, Set, TaskCard
from unitxt.test_utils.card import test_card

dataset_name = "claim_stance_topic"

class_names = [
    "advertising",
    "all nations a right to nuclear weapons",
    "a mandatory retirement age",
    "american jobs act",
    "asean",
    "atheism",
    "austerity measures",
    "barrier methods of contraception",
    "blasphemy",
    "boxing",
    "bribery",
    "burning the stars and stripes",
    "children",
    "collective bargaining rights claimed by trades unions",
    "congressional earmarks",
    "democratic governments should require voters to present photo identification at the polling station",
    "democratization",
    "endangered species",
    "enforce term limits on the legislative branch of government",
    "freedom of speech",
    "fund education using a voucher scheme",
    "gambling",
    "governments should choose open source software",
    "high rises for housing",
    "holocaust denial",
    "housewives should be paid for their work",
    "hydroelectric dams",
    "implement playoffs in collegiate level american football",
    "intellectual property rights",
    "israel's 2008-2009 military operations against gaza",
    "leaking of military documents",
    "multiculturalism",
    "national service",
    "only teach abstinence for sex education in schools",
    "open primaries",
    "partial birth abortions",
    "physical education",
    "poor communities",
    "raising the school leaving age to 18",
    "re-engage with myanmar",
    "the blockade of gaza",
    "the creation of private universities in the uk",
    "the free market",
    "the growing of tobacco",
    "the keystone xl pipeline",
    "the monarchy",
    "the one-child policy of the republic of china",
    "the right to asylum",
    "the right to bear arms",
    "the sale of violent video games to minors",
    "the use of affirmative action",
    "the use of performance enhancing drugs in professional sports",
    "the use of truth and reconciliation commissions",
    "wind power",
    "year round schooling",
]


card = TaskCard(
    loader=LoadHF(path="ibm/claim_stance", name=f"{dataset_name}"),
    preprocess_steps=[
        Set(
            fields={
                "classes": class_names,
                "text_type": "argument",  # TODO maybe text?
            }
        ),
    ],
    task="tasks.classification.multi_class.topic_classification",
    templates="templates.classification.multi_class.all",
    __tags__={
        "language": "en",
        "license": "cc-by-3.0",
        "region": "us",
        "size_categories": "1K<n<10K",
        "task_categories": "text-classification",
    },
    __description__=(
        "Claim Stance contains 2,394 labeled Wikipedia claims for 55 topics. The dataset includes the stance (Pro/Con) of each claim towards the topic, as well as fine-grained annotations, based on the semantic model of Stance Classification of Context-Dependent Claims (topic target, topic sentiment towards its target, claim target, claim sentiment towards its target, and the relation between the targets)… See the full description on the dataset page: https://huggingface.co/datasets/ibm/claim_stance."
    ),
)

test_card(card, debug=False)
add_to_catalog(artifact=card, name=f"cards.{dataset_name}", overwrite=True)
