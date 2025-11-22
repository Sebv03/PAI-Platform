# backend/app/models/__init__.py
# Importa todos los modelos aquí para que sean accesibles a través de 'from app.models import ...'
from .user import User
from .course import Course
from .enrollment import Enrollment
from .task import Task
from .submission import Submission
from .announcement import Announcement
from .comment import Comment
from .student_profile import StudentProfile
# Agrega aquí cualquier otro modelo nuevo que crees.