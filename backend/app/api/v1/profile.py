import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import (
    User, Profile, Education, Skill, Experience, Certification, Achievement, Project
)
from app.schemas.profile import (
    ProfileResponse, ProfileUpdate, ProfileCreate,
    EducationCreate, EducationUpdate, EducationResponse,
    SkillCreate, SkillUpdate, SkillResponse,
    ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    CertificationCreate, CertificationUpdate, CertificationResponse,
    AchievementCreate, AchievementUpdate, AchievementResponse
)

router = APIRouter()

# --- PROFILE (Master Profile details) ---

@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id).options(
        selectinload(Profile.educations),
        selectinload(Profile.skills),
        selectinload(Profile.experiences),
        selectinload(Profile.certifications),
        selectinload(Profile.achievements),
        selectinload(Profile.projects).selectinload(Project.analysis)
    )
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create one."
        )
    return profile

@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")

    profile = Profile(
        user_id=current_user.id,
        **profile_in.model_dump()
    )
    db.add(profile)
    await db.commit()
    return await get_profile(current_user, db)

@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    for field, value in profile_in.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    await db.commit()
    return await get_profile(current_user, db)


# --- EDUCATION ROUTES ---

@router.post("/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def add_education(
    edu_in: EducationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create profile first.")

    education = Education(
        profile_id=profile.id,
        **edu_in.model_dump()
    )
    db.add(education)
    await db.commit()
    return education

@router.put("/education/{edu_id}", response_model=EducationResponse)
async def update_education(
    edu_id: uuid.UUID,
    edu_in: EducationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if education belongs to user profile
    stmt = select(Education).join(Profile).where(
        Education.id == edu_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    edu = res.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="Education record not found.")

    for field, value in edu_in.model_dump(exclude_unset=True).items():
        setattr(edu, field, value)
    await db.commit()
    return edu

@router.delete("/education/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    edu_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Education).join(Profile).where(
        Education.id == edu_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    edu = res.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="Education record not found.")

    await db.delete(edu)
    await db.commit()
    return None


# --- SKILLS ROUTES ---

@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def add_skill(
    skill_in: SkillCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    skill = Skill(profile_id=profile.id, **skill_in.model_dump())
    db.add(skill)
    await db.commit()
    return skill

@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: uuid.UUID,
    skill_in: SkillUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Skill).join(Profile).where(
        Skill.id == skill_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    skill = res.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found.")

    for field, value in skill_in.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)
    await db.commit()
    return skill

@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Skill).join(Profile).where(
        Skill.id == skill_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    skill = res.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found.")

    await db.delete(skill)
    await db.commit()
    return None


# --- EXPERIENCE ROUTES ---

@router.post("/experience", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def add_experience(
    exp_in: ExperienceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    exp = Experience(profile_id=profile.id, **exp_in.model_dump())
    db.add(exp)
    await db.commit()
    return exp

@router.put("/experience/{exp_id}", response_model=ExperienceResponse)
async def update_experience(
    exp_id: uuid.UUID,
    exp_in: ExperienceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Experience).join(Profile).where(
        Experience.id == exp_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    exp = res.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience record not found.")

    for field, value in exp_in.model_dump(exclude_unset=True).items():
        setattr(exp, field, value)
    await db.commit()
    return exp

@router.delete("/experience/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    exp_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Experience).join(Profile).where(
        Experience.id == exp_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    exp = res.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience record not found.")

    await db.delete(exp)
    await db.commit()
    return None


# --- CERTIFICATIONS ROUTES ---

@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
async def add_certification(
    cert_in: CertificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    cert = Certification(profile_id=profile.id, **cert_in.model_dump())
    db.add(cert)
    await db.commit()
    return cert

@router.put("/certifications/{cert_id}", response_model=CertificationResponse)
async def update_certification(
    cert_id: uuid.UUID,
    cert_in: CertificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Certification).join(Profile).where(
        Certification.id == cert_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    cert = res.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found.")

    for field, value in cert_in.model_dump(exclude_unset=True).items():
        setattr(cert, field, value)
    await db.commit()
    return cert

@router.delete("/certifications/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(
    cert_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Certification).join(Profile).where(
        Certification.id == cert_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    cert = res.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found.")

    await db.delete(cert)
    await db.commit()
    return None


# --- ACHIEVEMENTS ROUTES ---

@router.post("/achievements", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
async def add_achievement(
    ach_in: AchievementCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    res = await db.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    ach = Achievement(profile_id=profile.id, **ach_in.model_dump())
    db.add(ach)
    await db.commit()
    return ach

@router.put("/achievements/{ach_id}", response_model=AchievementResponse)
async def update_achievement(
    ach_id: uuid.UUID,
    ach_in: AchievementUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Achievement).join(Profile).where(
        Achievement.id == ach_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    ach = res.scalar_one_or_none()
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found.")

    for field, value in ach_in.model_dump(exclude_unset=True).items():
        setattr(ach, field, value)
    await db.commit()
    return ach

@router.delete("/achievements/{ach_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(
    ach_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Achievement).join(Profile).where(
        Achievement.id == ach_id, Profile.user_id == current_user.id
    )
    res = await db.execute(stmt)
    ach = res.scalar_one_or_none()
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found.")

    await db.delete(ach)
    await db.commit()
    return None
