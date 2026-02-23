from django.core.management.base import BaseCommand
from automation.service.workflow_runner import WorkFlowRunner
from automation.logging.logger import get_logger

logger = get_logger("Command")


class Command(BaseCommand):
    help = "Run Playwright automation workflow"

    def handle(self, *args, **kwargs):
        logger.info("Command started")
        self.stdout.write(self.style.SUCCESS("Starting automation workflow..."))

        try:
            runner = WorkFlowRunner()
            result = runner.run_user_workflow()
            self.stdout.write(
                self.style.SUCCESS(f"Workflow finished with status: {result['status']}")
            )
            logger.info("Command completed")
        except Exception as e:
            logger.error(str(e))
            self.stdout.write(self.style.ERROR(f"Workflow failed: {str(e)}"))
