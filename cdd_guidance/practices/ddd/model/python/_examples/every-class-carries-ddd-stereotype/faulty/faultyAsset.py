# <<Aggregate Root>> <<Entity>>
class Subscription:
    def change_plan(self, plan: "Plan") -> None:
        self.plan = plan


class Plan:
    id: str
    name: str
