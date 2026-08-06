import logging

logging.basicConfig(

    filename="logs/sentinel.log",

    level=logging.INFO,

    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("Sentinel")
