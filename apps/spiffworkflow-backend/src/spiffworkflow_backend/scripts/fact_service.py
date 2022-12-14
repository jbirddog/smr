"""Fact_service."""
from typing import Any
from typing import Optional

from SpiffWorkflow import Task as SpiffTask  # type: ignore

from spiffworkflow_backend.scripts.script import Script


class FactService(Script):
    """FactService."""

    def get_description(self) -> str:
        """Get_description."""
        return """Just your basic class that can pull in data from a few api endpoints and
        do a basic task."""

    def run(
        self,
        task: Optional[SpiffTask],
        environment_identifier: str,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Run."""
        if "type" not in kwargs:
            raise Exception("Please specify a 'type' of fact as a keyword argument.")
        else:
            fact = kwargs["type"]

        if fact == "cat":
            details = "The cat in the hat"  # self.get_cat()
        elif fact == "norris":
            details = "Chuck Norris doesn’t read books. He stares them down until he gets the information he wants."
        elif fact == "buzzword":
            details = "Move the Needle."  # self.get_buzzword()
        else:
            details = "unknown fact type."

        # self.add_data_to_task(task, details)
        return details
