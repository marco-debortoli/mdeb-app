from app.database import Base  # noqa: F401

# Import all models here so Alembic can detect them for migrations.
from app.models.task import Category, Project, Task, TaskNote  # noqa: F401
from app.models.journal import JournalEntry, DayRating  # noqa: F401
from app.models.finance import FinanceAccount, AccountValue, FinanceCategory, Merchant, Transaction  # noqa: F401
from app.models.time_tracking import TimeCategory, TimeSubcategory, TimeEntry  # noqa: F401
from app.models.notes import NoteFolder, Note  # noqa: F401
