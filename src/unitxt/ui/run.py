from functools import lru_cache

import gradio as gr

from unitxt.ui import constants as cons
from unitxt.ui.ui_tiny_utils import *
from unitxt.ui.ui_utils import (
    build_command,
    create_dataframe,
    data,
    decrease_num,
    get_catalog_items,
    get_predictions_and_scores,
    get_prompts,
    get_templates,
    hash_dict,
    increase_num,
    jsons,
    update_choices_per_task,
)


def run_unitxt_entry(
    task,
    dataset,
    template,
    instruction=None,
    format=None,
    num_demos=0,
    augmentor=None,
    index=1,
    run_model=False,
):
    is_dataset = isinstance(dataset, str)
    is_template = isinstance(template, str)
    if not is_dataset or not is_template:
        if is_dataset:
            msg = "Please select a template"
        else:
            msg = "Please select Dataset Card and a template"

        return msg, "", "", cons.EMPTY_SCORES_FRAME, cons.EMPTY_SCORES_FRAME, ""

    if not isinstance(instruction, str):
        instruction = None
    if not isinstance(format, str):
        format = None
    if not isinstance(num_demos, int):
        num_demos = 0
    if not isinstance(augmentor, str):
        augmentor = None
    if not isinstance(index, int):
        index = 1
    # if not isinstance(max_new_tokens, float):
    #     max_new_tokens = cons.MAX_NEW_TOKENS
    return run_unitxt(
        dataset,
        template,
        instruction,
        format,
        num_demos,
        augmentor,
        run_model,
        index,
        # max_new_tokens,
    )


@lru_cache
def run_unitxt(
    dataset,
    template,
    instruction=None,
    format=None,
    num_demos=0,
    augmentor=None,
    run_model=False,
    index=1,
    # max_new_tokens=cons.MAX_NEW_TOKENS,
):
    index = index - 1
    try:
        prompts_list, prompt_args = get_prompts(
            dataset, template, num_demos, instruction, format, augmentor
        )
        selected_prompt = prompts_list[index]
        prompt_text = selected_prompt[cons.PROMPT_SOURCE_STR]
        prompt_target = selected_prompt[cons.PROPT_TARGET_STR]
        command = build_command(prompt_args, with_prediction=run_model)
    except Exception as e:
        prompt_text = f"""
    Oops... this combination didnt work! Try something else.

    Exception: {e!r}
    """
        prompt_target = ""
        command = ""
    selected_prediction = ""
    instance_result = cons.EMPTY_SCORES_FRAME
    agg_result = cons.EMPTY_SCORES_FRAME
    if run_model:
        try:
            predictions, results = get_predictions_and_scores(
                tuple(hash_dict(prompt) for prompt in prompts_list)
            )
            selected_prediction = predictions[index]
            selected_result = results[index]["score"]
            instance_result = create_dataframe(selected_result["instance"])
            agg_result = create_dataframe(selected_result["global"])
        except Exception as e:
            selected_prediction = f"""
            An exception has occured:

            {e!r}
            """

    return (
        prompt_text,
        prompt_target,
        selected_prediction,
        instance_result,
        agg_result,
        command,
    )


def display_json(element, cards, templates, instructions, formats):
    def get_json(element_key, value):
        if isinstance(value, str):
            if value in jsons:
                to_print = jsons[value]
                if "loader" in to_print:
                    if "path" in to_print["loader"]:
                        to_print["loader"][" path"] = to_print["loader"].pop("path")
                return to_print

            else:
                return {"": f"Error: {value}'s json not found"}
        else:
            return {"": f"Select {element_key} to view json"}

    if element == cons.DATASET_CARD:
        element_name = cards
    elif element == cons.TEMPLATE:
        element_name = templates
    elif element == cons.FORMAT:
        element_name = formats
    elif element == cons.INSTRUCTION:
        element_name = instructions
    message = get_json(element, element_name)
    return element_name, message


def display_json_button(element):
    if element in jsons:
        json_el = jsons[element]
        if "loader" in json_el:
            if "path" in json_el["loader"]:
                json_el["loader"][" path"] = json_el["loader"].pop("path")
        return (
            go_to_json_tab(),
            make_mrk_down_invisible(),
            make_txt_visible(element),
            make_json_visible(json_el),
        )

    else:
        return tabs, f"Error: {element}'s json not found", None, None


######################
### UI STARTS HERE ###
######################

demo = gr.Blocks()

with demo:
    with gr.Row():
        # LOGO
        logo = gr.Image(
            cons.BANNER_PATH,
            show_label=False,
            show_download_button=False,
            show_share_button=False,
            scale=0.3333,
        )
        links = gr.Markdown(value=cons.INTRO_TXT)

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group() as buttons_group:
                tasks = gr.Dropdown(choices=sorted(data.keys()), label="Task", scale=3)
                cards = gr.Dropdown(choices=[], label="Dataset Card", scale=9)
                cards_js_button = gr.Button(
                    cons.JSON_BUTTON_TXT,
                    scale=1,
                    size="sm",
                    min_width=0.1,
                    interactive=False,
                    variant="secondary",
                )

                templates = gr.Dropdown(choices=[], label="Template", scale=9)
                templates_js_button = gr.Button(
                    cons.JSON_BUTTON_TXT,
                    scale=1,
                    size="sm",
                    min_width=0.1,
                    interactive=False,
                    variant="secondary",
                )

                instructions = gr.Dropdown(
                    choices=[None, *get_catalog_items("instructions")[0]],
                    label="Instruction",
                    scale=5,
                )
                instructions_js_button = gr.Button(
                    cons.JSON_BUTTON_TXT,
                    scale=1,
                    size="sm",
                    min_width=1,
                    interactive=False,
                )
                formats = gr.Dropdown(
                    choices=[None, *get_catalog_items("formats")[0]],
                    label="Format",
                    scale=5,
                )
                formats_js_button = gr.Button(
                    cons.JSON_BUTTON_TXT,
                    scale=1,
                    size="sm",
                    min_width=1,
                    interactive=False,
                )

                num_shots = gr.Slider(label="Num Shots", maximum=5, step=1, value=0)
                with gr.Accordion(label="Additional Parameters", open=False):
                    augmentors = gr.Dropdown(choices=[], label="Augmentor")

            generate_prompts_button = gr.Button(
                value="Generate Prompts", interactive=False
            )
            infer_button = gr.Button(
                value=f"Infer with {cons.FLAN_T5_BASE}", interactive=False
            )
            clear_fields = gr.ClearButton()

        with gr.Column(scale=3):
            with gr.Tabs() as tabs:
                with gr.TabItem("Intro", id="intro"):
                    main_intro = gr.Markdown(cons.MAIN_INTRO_TXT)
                with gr.TabItem("Demo", id="demo"):
                    with gr.Row():
                        previous_sample = gr.Button(
                            "Previous sample", interactive=False
                        )
                        next_sample = gr.Button("Next Sample", interactive=False)
                    with gr.Accordion():
                        with gr.Group() as prompt_group:
                            prompts_title = gr.Markdown("## Prompts:")
                            selected_prompt = gr.Textbox(
                                lines=5,
                                show_copy_button=True,
                                label="Prompt",
                                autoscroll=False,
                            )

                            target = gr.Textbox(lines=1, label="Target", scale=3)

                    with gr.Group(visible=False) as infer_group:
                        infer_title = gr.Markdown("## Inference:")
                        prediction = gr.Textbox(
                            lines=1,
                            label="Model prediction",
                            value=" ",
                            autoscroll=False,
                        )
                        with gr.Row():
                            instance_scores = gr.DataFrame(
                                label="Instance scores",
                                value=cons.EMPTY_SCORES_FRAME,
                                headers=cons.SCORE_FRAME_HEADERS,
                                height=200,
                            )
                            global_scores = gr.DataFrame(
                                label=f"Aggregated scores for {cons.PROMPT_SAMPLE_SIZE} predictions",
                                value=cons.EMPTY_SCORES_FRAME,
                                headers=cons.SCORE_FRAME_HEADERS,
                                height=200,
                            )
                with gr.TabItem("Code", id="code"):
                    code_intro = gr.Markdown(value=cons.CODE_INTRO_TXT)
                    code = gr.Code(language="python", lines=1)
                with gr.TabItem("View Catalog", id="json"):
                    json_intro = gr.Markdown(value=cons.JSON_INTRO_TXT)
                    element_name = gr.Text(label="Selected Item:", visible=False)
                    json_viewer = gr.Json(value=None, visible=False)

    # INVISIBLE ELEMENTS FOR VALUE STORAGE
    run_model = gr.Checkbox(value=False, visible=False)
    sample_choice = gr.Number(value=0, visible=False)

    # DROPDOWNS AND JSON BUTTONS LOGIC
    tasks.select(update_choices_per_task, inputs=tasks, outputs=[cards, augmentors])
    cards.select(get_templates, inputs=[tasks, cards], outputs=templates).then(
        activate_button, outputs=cards_js_button
    )
    cards_js_button.click(
        display_json_button, cards, [tabs, json_intro, element_name, json_viewer]
    ).then(deactivate_button, outputs=cards_js_button)
    templates.select(activate_button, outputs=templates_js_button).then(
        activate_button, outputs=generate_prompts_button
    ).then(deactivate_button, outputs=infer_button)
    templates_js_button.click(
        display_json_button, templates, [tabs, json_intro, element_name, json_viewer]
    ).then(deactivate_button, outputs=templates_js_button)
    instructions.select(activate_button, outputs=instructions_js_button).then(
        activate_button, outputs=generate_prompts_button
    ).then(deactivate_button, outputs=infer_button)
    instructions_js_button.click(
        display_json_button, instructions, [tabs, json_intro, element_name, json_viewer]
    ).then(deactivate_button, outputs=instructions_js_button)
    formats.select(activate_button, outputs=formats_js_button).then(
        activate_button, outputs=generate_prompts_button
    ).then(deactivate_button, outputs=infer_button)
    formats_js_button.click(
        display_json_button, formats, [tabs, json_intro, element_name, json_viewer]
    ).then(deactivate_button, outputs=formats_js_button)
    num_shots.change(activate_button, outputs=generate_prompts_button).then(
        deactivate_button, outputs=infer_button
    )
    augmentors.select(activate_button, outputs=generate_prompts_button).then(
        deactivate_button, outputs=infer_button
    )

    parameters = [
        tasks,
        cards,
        templates,
        instructions,
        formats,
        num_shots,
        augmentors,
        sample_choice,
        run_model,
    ]

    outputs = {
        selected_prompt,
        target,
        prediction,
        instance_scores,
        global_scores,
        code,
    }

    # CLEAR BUTTON LOGIC
    clear_fields.click(lambda: [None] * len(parameters), outputs=parameters).then(
        run_unitxt_entry, parameters, outputs=outputs
    ).then(make_mrk_down_visible, outputs=code_intro).then(
        go_to_intro_tab, outputs=tabs
    ).then(make_group_invisible, outputs=infer_group).then(
        deactivate_button, outputs=generate_prompts_button
    ).then(deactivate_button, outputs=infer_button).then(
        deactivate_button, outputs=previous_sample
    ).then(deactivate_button, outputs=next_sample)

    # GENERATE PROMPT BUTTON LOGIC
    generate_prompts_button.click(
        deactivate_button, outputs=generate_prompts_button
    ).then(make_group_invisible, outputs=infer_group).then(
        go_to_main_tab, outputs=tabs
    ).then(make_mrk_down_invisible, outputs=code_intro).then(
        run_unitxt_entry, parameters, outputs=outputs
    ).then(activate_button, outputs=infer_button).then(
        activate_button, outputs=previous_sample
    ).then(activate_button, outputs=next_sample)

    # INFER BUTTON LOGIC
    infer_button.click(make_group_visible, outputs=infer_group).then(
        deactivate_button, outputs=infer_button
    ).then(go_to_main_tab, outputs=tabs).then(
        make_mrk_down_invisible, outputs=code_intro
    ).then(select_checkbox, outputs=run_model).then(
        run_unitxt_entry, parameters, outputs=outputs
    )

    # SAMPLE CHOICE LOGIC
    next_sample.click(increase_num, sample_choice, sample_choice)
    previous_sample.click(decrease_num, sample_choice, sample_choice)
    sample_choice.change(run_unitxt_entry, parameters, outputs=outputs)

if __name__ == "__main__":
    demo.launch(debug=True)