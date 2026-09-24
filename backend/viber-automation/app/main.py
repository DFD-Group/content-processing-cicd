import datetime
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
from app.api_models import CreateViberJobRequest
from app.database import get_session
from app.entities import ViberJob
from app.middleware.api_key_auth import verify_api_key
from app.viber_client import prepare_viber_message

app = FastAPI(dependencies=[Depends(verify_api_key)])


@app.get("/health")
def health():
    return {"status": "UP"}


def require_scope(scope: str):
    async def checker(request: Request):
        key_info = getattr(request.state, "api_key_metadata", None)

        if not key_info or scope not in key_info.get("scopes", []):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required scope: {scope}",
            )

    return checker


@app.post(
    "/viber/jobs",
    status_code=202,
    dependencies=[Depends(require_scope("content:write"))],
)
def create_viber_job(
    data: CreateViberJobRequest,
    session: Session = Depends(get_session),
):
    message = (
        "Привет,\n"
        "\n"
        "Изпратих поръчка за:\n"
        "\n"
        f"- Размер: {data.plate_size}\n"
        f"- Надпис: “{data.sign}”\n"
        f"- Количество: {data.plate_count}\n"
        "\n"
        "Макетът е потвърден.\n"
        "\n"
        f"Експедицията на камиона {data.dfd_order_number}, "
        f"към който принадлежи тази поръчка, ще бъде на "
        f"{data.expedition_date.strftime('%d.%m.%Y')}."
    )

    job = ViberJob(
        plate_size=data.plate_size,
        plate_sign=data.sign,
        plate_count=data.plate_count,
        dfd_order_number=data.dfd_order_number,
        expedition_date=data.expedition_date,
        message_text=message,
        status="pending",
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    try:
        prepare_viber_message(message)

        job.status = "sent"
        job.sent_at = datetime.datetime.now(datetime.timezone.utc)
        job.error_message = None

        session.commit()
        session.refresh(job)

    except Exception as error:
        job.status = "failed"
        job.error_message = str(error)
        session.commit()
        session.refresh(job)

        raise HTTPException(
            status_code=500,
            detail={
                "id": str(job.id),
                "status": job.status,
                "error": job.error_message,
            },
        )

    return {
        "id": str(job.id),
        "status": job.status,
    }