from automation.logging.logger import get_logger
from automation.playwright.core.browser_manager import BrowserManager
from automation.playwright.workflow.user_workflow import UserWorkflow

logger = get_logger("WorkFlowRunner")


class WorkFlowRunner:
    def run_user_workflow(self):
        logger.info("Starting user workflow...")

        with BrowserManager() as page:
            workflow = UserWorkflow(page)
            result = workflow.run()

            logger.info("Saving result to DB")
            return result
