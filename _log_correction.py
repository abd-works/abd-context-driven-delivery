from context_tools.cdd.cdd import Cdd

host = Cdd(
    fidelity="discovery",
    path=r"c:\Users\jeffa\OneDrive - abd.works\personal\paradise-mobile\pml-domain",
    session="pml-domain-tests",
)
host.repairer.start(
    asset="tests/domain/.context/domain-model.drawio",
    violation="(diagram) class-title-no-markdown-bold",
)
print(
    host.repairer.log_correction(
        entry_id="c96dd33c",
        improved=(
            "Scanner class-title-no-markdown-bold flags markdown ** in class "
            "titles; Drawio rule documents plain text inside <b>. Generator "
            "already strips via _display_class_name."
        ),
        status="fixed",
    )
)
