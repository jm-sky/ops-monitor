# Plan Implementacji: Globalny Katalog Przedmiotów

## 📋 Przegląd

Plan implementacji globalnego katalogu przedmiotów zgodnie z wymaganiami z ROADMAP_ONLINE.md. Globalny katalog to baza szablonów przedmiotów, które użytkownicy mogą dodawać do swoich kontenerów.

**Ważne rozróżnienie:**
- **Globalny katalog** = źródło szablonów przedmiotów (niezależne od przedmiotów użytkownika)
- **Linkowanie** = mechanizm synchronizacji między przedmiotami użytkownika w różnych kontenerach (już zaimplementowane przez `linkedItemId`)
- Gdy użytkownik dodaje przedmiot z globalnego katalogu, tworzy się **niezależna kopia**, którą może swobodnie edytować
- Jeśli użytkownik doda ten sam przedmiot do dwóch kontenerów, są one **linkowane między sobą** (nie z katalogiem)

## 🎯 Cele

1. **Backend**: Tabela `global_catalogue_items` z wersjonowaniem przedmiotów
2. **Backend**: Endpointy API do przeglądania katalogu (wyszukiwanie, filtrowanie)
3. **Backend**: Endpoint do dodawania przedmiotów z katalogu do kontenera użytkownika
4. **Backend**: Zarządzanie katalogiem (dodawanie/edycja przez adminów lub użytkowników)
5. **Frontend**: Przeglądarka przedmiotów (globalny katalog)
6. **Frontend**: Autocomplete przy dodawaniu itemu z globalnego katalogu
7. **Frontend**: UI do zarządzania katalogiem (dla adminów)

## 🔍 Analiza Obecnego Stanu

### Backend

**Istniejące modele:**
- `GearItemDB` w `backend/app/modules/gear/db_models.py`
- `GearContainerDB` w `backend/app/modules/gear/db_models.py`
- Brak tabeli `global_catalogue_items`

**Istniejące endpointy:**
- `POST /gear/containers/{container_id}/items` - tworzenie przedmiotu
- `GET /gear/containers/{container_id}/items` - pobieranie przedmiotów kontenera
- `GET /gear/items/{item_id}` - pobieranie przedmiotu

**Brakujące:**
- Tabela `global_catalogue_items` z wersjonowaniem
- Endpointy do przeglądania katalogu
- Endpoint do dodawania przedmiotu z katalogu do kontenera

### Frontend

**Istniejące komponenty:**
- `ItemFormPage.vue` - formularz dodawania/edycji przedmiotu (już ma tabs: "new" i "catalog" - przedmioty użytkownika)
- `ItemFormFields.vue` - pola formularza
- `ItemCatalogSelector.vue` - autocomplete z przedmiotami użytkownika (tab "catalog")
- Linkowanie przedmiotów użytkownika (już zaimplementowane przez `linkedItemId`)

**Brakujące:**
- Trzeci tab w ItemFormPage dla globalnego katalogu
- Nowy komponent `GlobalCatalogueSelector.vue` lub rozszerzenie `ItemCatalogSelector.vue`
- Przeglądarka globalnego katalogu
- UI do zarządzania katalogiem (dla adminów)

## 📝 Plan Implementacji

### Faza 1: Backend - Model Danych i Migracja

#### Step 1.1: Utworzenie modelu `GlobalCatalogueItemDB`

**File:** `backend/app/modules/gear/db_models.py`

**Krok 1a: Dodaj nowy model (przed końcem pliku):**

```python
class GlobalCatalogueItemDB(Base):
    """SQLAlchemy model for global catalogue items.

    Represents template items in the global catalogue that users can add to their containers.
    Items from the catalogue are copied (not linked) when added to user containers.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        version: Version number for this item (for versioning support)
        name: Item name
        category: Item category (water, food, shelter, etc.)
        weight: Item weight value
        weight_unit: Weight unit (g, kg, oz, or lb)
        description: Item description
        brand: Manufacturer/brand
        model: Model name/number
        price_tier: Price tier (low, medium, high)
        quality: Quality tier (low, medium, high) - zgodne z GearItemQuality
        url: Product URL
        color: Item color (optional)
        is_active: Whether item is active in catalogue
        created_by: User ID who created this item (nullable for system items)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "global_catalogue_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    weight_unit: Mapped[str] = mapped_column(String(5), nullable=False, default="g")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    quality: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high (zgodne z GearItemQuality)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationships
    creator: Mapped["UserDB | None"] = relationship("UserDB", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<GlobalCatalogueItemDB(id={self.id}, name={self.name}, version={self.version})>"
```

**Krok 1b: Dodaj indeksy dla wyszukiwania:**

```python
# W __table_args__ lub osobna migracja:
# CREATE INDEX ix_global_catalogue_items_name ON global_catalogue_items(name);
# CREATE INDEX ix_global_catalogue_items_category ON global_catalogue_items(category);
# CREATE INDEX ix_global_catalogue_items_brand ON global_catalogue_items(brand);
# CREATE INDEX ix_global_catalogue_items_is_active ON global_catalogue_items(is_active);
```

#### Step 1.2: Utworzenie migracji

**File:** `backend/migrations/029_add_global_catalogue_items.py`

**Uwaga:** Użyj formatu async z `text()` zgodnie z istniejącymi migracjami (np. `027_add_container_ratings.py`):

```python
"""Migration: Add global_catalogue_items table.

This migration adds the global_catalogue_items table for storing template items
that users can add to their containers.

Usage:
    python migrations/029_add_global_catalogue_items.py upgrade
    python migrations/029_add_global_catalogue_items.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Create global_catalogue_items table."""
    print("Creating global_catalogue_items table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "global_catalogue_items")

        if table_exist:
            print("global_catalogue_items table already exists, skipping migration...")
            return

        print("Creating global_catalogue_items table...")
        await conn.execute(
            text(
                """
                CREATE TABLE global_catalogue_items (
                    id VARCHAR(36) PRIMARY KEY,
                    version INTEGER NOT NULL DEFAULT 1,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    weight FLOAT NOT NULL,
                    weight_unit VARCHAR(5) NOT NULL DEFAULT 'g',
                    description TEXT,
                    brand VARCHAR(255),
                    model VARCHAR(255),
                    price_tier VARCHAR(20),
                    quality VARCHAR(20),
                    url TEXT,
                    color VARCHAR(50),
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    created_by VARCHAR(36),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_global_catalogue_items_created_by 
                        FOREIGN KEY (created_by) 
                        REFERENCES users(id) 
                        ON DELETE SET NULL
                );
            """
            ),
        )

        # Create indexes
        print("Creating indexes...")
        await conn.execute(
            text("CREATE INDEX ix_global_catalogue_items_name ON global_catalogue_items(name);")
        )
        await conn.execute(
            text("CREATE INDEX ix_global_catalogue_items_category ON global_catalogue_items(category);")
        )
        await conn.execute(
            text("CREATE INDEX ix_global_catalogue_items_brand ON global_catalogue_items(brand);")
        )
        await conn.execute(
            text("CREATE INDEX ix_global_catalogue_items_is_active ON global_catalogue_items(is_active);")
        )

        print("Migration completed successfully!")


#### Step 1.4: Dodanie kolumny `catalogue_item_id` do `gear_items`

**File:** `backend/migrations/030_add_catalogue_item_id_to_gear_items.py`

**Uwaga:** Ta migracja dodaje pole `catalogue_item_id` do istniejącej tabeli `gear_items`, aby móc śledzić, które przedmioty pochodzą z katalogu.

```python
"""Migration: Add catalogue_item_id to gear_items table.

This migration adds the catalogue_item_id column to gear_items table
to track which items were added from the global catalogue.

Usage:
    python migrations/030_add_catalogue_item_id_to_gear_items.py upgrade
    python migrations/030_add_catalogue_item_id_to_gear_items.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Add catalogue_item_id column to gear_items table."""
    print("Adding catalogue_item_id column to gear_items table...")

    async with engine.begin() as conn:
        column_exist = await column_exists(conn, "gear_items", "catalogue_item_id")

        if column_exist:
            print("catalogue_item_id column already exists, skipping migration...")
            return

        print("Adding catalogue_item_id column...")
        await conn.execute(
            text(
                """
                ALTER TABLE gear_items
                ADD COLUMN catalogue_item_id VARCHAR(36),
                ADD CONSTRAINT fk_gear_items_catalogue_item_id 
                    FOREIGN KEY (catalogue_item_id) 
                    REFERENCES global_catalogue_items(id) 
                    ON DELETE SET NULL;
            """
            ),
        )

        # Create index for better query performance
        print("Creating index...")
        await conn.execute(
            text("CREATE INDEX ix_gear_items_catalogue_item_id ON gear_items(catalogue_item_id);")
        )

        print("Migration completed successfully!")


async def downgrade() -> None:
    """Remove catalogue_item_id column from gear_items table."""
    print("Removing catalogue_item_id column from gear_items table...")

    async with engine.begin() as conn:
        column_exist = await column_exists(conn, "gear_items", "catalogue_item_id")

        if not column_exist:
            print("catalogue_item_id column does not exist, skipping downgrade...")
            return

        # Drop index
        print("Dropping index...")
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_gear_items_catalogue_item_id;")
        )

        # Drop foreign key constraint
        print("Dropping foreign key constraint...")
        await conn.execute(
            text("ALTER TABLE gear_items DROP CONSTRAINT IF EXISTS fk_gear_items_catalogue_item_id;")
        )

        # Drop column
        print("Dropping column...")
        await conn.execute(
            text("ALTER TABLE gear_items DROP COLUMN IF EXISTS catalogue_item_id;")
        )

        print("Downgrade completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
```

#### Step 1.5: Utworzenie modelu `CatalogueItemImageDB`

**File:** `backend/app/modules/gear/db_models.py`

**Uwaga:** Model identyczny z `ItemImageDB`, ale dla przedmiotów katalogu. Obrazki katalogu wymagają autoryzacji (nie są publiczne).

```python
class CatalogueItemImageDB(Base):
    """SQLAlchemy model for catalogue item images.

    Represents images uploaded for global catalogue items.
    Identical structure to ItemImageDB, but for catalogue items.

    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        catalogue_item_id: Parent catalogue item ID
        user_id: Uploader user ID (admin)
        storage_type: Storage backend type (local or s3)
        file_path: Relative path for local storage, S3 key for S3
        file_name: Original filename
        file_size: File size in bytes
        mime_type: MIME type (image/jpeg, image/png, etc.)
        width: Image width in pixels
        height: Image height in pixels
        is_primary: Whether this is the primary image for the item
        order: Display order (0-based)
        is_processed: Whether image has been processed (resized/optimized)
        original_file_size: Original file size before processing
        external_url: External URL if not hosted locally
        created_at: Upload timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "catalogue_item_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    catalogue_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("global_catalogue_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Storage info
    storage_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Image metadata
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Processing flags
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    original_file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    catalogue_item: Mapped["GlobalCatalogueItemDB"] = relationship("GlobalCatalogueItemDB", back_populates="images")
    user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<CatalogueItemImageDB(id={self.id}, catalogue_item_id={self.catalogue_item_id}, file_name={self.file_name})>"


# Add images relationship to GlobalCatalogueItemDB
GlobalCatalogueItemDB.images = relationship(
    "CatalogueItemImageDB",
    back_populates="catalogue_item",
    cascade="all, delete-orphan",
    order_by="CatalogueItemImageDB.order",
)
```

**Migracja dla tabeli `catalogue_item_images`:**

**File:** `backend/migrations/031_add_catalogue_item_images_table.py`

```python
"""Migration: Add catalogue_item_images table.

This migration adds the catalogue_item_images table for storing images
for global catalogue items.

Usage:
    python migrations/031_add_catalogue_item_images_table.py upgrade
    python migrations/031_add_catalogue_item_images_table.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Create catalogue_item_images table."""
    print("Creating catalogue_item_images table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "catalogue_item_images")

        if table_exist:
            print("catalogue_item_images table already exists, skipping migration...")
            return

        print("Creating catalogue_item_images table...")
        await conn.execute(
            text(
                """
                CREATE TABLE catalogue_item_images (
                    id VARCHAR(36) PRIMARY KEY,
                    catalogue_item_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36) NOT NULL,
                    storage_type VARCHAR(10) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type VARCHAR(50) NOT NULL,
                    external_url VARCHAR(1000),
                    width INTEGER,
                    height INTEGER,
                    is_primary BOOLEAN NOT NULL DEFAULT false,
                    "order" INTEGER NOT NULL DEFAULT 0,
                    is_processed BOOLEAN NOT NULL DEFAULT false,
                    original_file_size INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_catalogue_item_images_catalogue_item_id 
                        FOREIGN KEY (catalogue_item_id) 
                        REFERENCES global_catalogue_items(id) 
                        ON DELETE CASCADE,
                    CONSTRAINT fk_catalogue_item_images_user_id 
                        FOREIGN KEY (user_id) 
                        REFERENCES users(id)
                );
            """
            ),
        )

        # Create indexes
        print("Creating indexes...")
        await conn.execute(
            text("CREATE INDEX ix_catalogue_item_images_catalogue_item_id ON catalogue_item_images(catalogue_item_id);")
        )
        await conn.execute(
            text("CREATE INDEX ix_catalogue_item_images_user_id ON catalogue_item_images(user_id);")
        )

        print("Migration completed successfully!")


async def downgrade() -> None:
    """Drop catalogue_item_images table."""
    print("Dropping catalogue_item_images table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "catalogue_item_images")

        if not table_exist:
            print("catalogue_item_images table does not exist, skipping downgrade...")
            return

        # Drop indexes
        print("Dropping indexes...")
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_catalogue_item_images_user_id;")
        )
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_catalogue_item_images_catalogue_item_id;")
        )

        # Drop table
        print("Dropping table...")
        await conn.execute(text("DROP TABLE IF EXISTS catalogue_item_images;"))

        print("Downgrade completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
```


async def downgrade() -> None:
    """Drop global_catalogue_items table."""
    print("Dropping global_catalogue_items table...")

    async with engine.begin() as conn:
        table_exist = await table_exists(conn, "global_catalogue_items")

        if not table_exist:
            print("global_catalogue_items table does not exist, skipping downgrade...")
            return

        # Drop indexes
        print("Dropping indexes...")
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_global_catalogue_items_is_active;")
        )
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_global_catalogue_items_brand;")
        )
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_global_catalogue_items_category;")
        )
        await conn.execute(
            text("DROP INDEX IF EXISTS ix_global_catalogue_items_name;")
        )

        # Drop table
        print("Dropping table...")
        await conn.execute(text("DROP TABLE IF EXISTS global_catalogue_items;"))

        print("Downgrade completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
```

#### Step 1.3: Utworzenie schematów Pydantic

**File:** `backend/app/modules/gear/schemas.py`

**Uwaga:** Trzeba również zaktualizować istniejące schematy `ItemCreate`, `ItemUpdate` i `ItemResponse` o pole `catalogueItemId`:

```python
# W ItemCreate, ItemUpdate, ItemResponse:
catalogueItemId: str | None = Field(None, alias="catalogueItemId", description="Reference to global catalogue item")
```

```python
class GlobalCatalogueItemBase(BaseModel):
    """Base schema for global catalogue items."""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    weight: float = Field(..., gt=0)
    weight_unit: GearWeightUnit = Field(default="g")
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    model: str | None = Field(None, max_length=255)
    price_tier: str | None = Field(None, pattern="^(low|medium|high)$")
    quality: GearItemQuality | None = None  # Użyj istniejącego typu GearItemQuality (low, medium, high)
    url: str | None = None
    color: str | None = Field(None, max_length=50)


class GlobalCatalogueItemCreate(GlobalCatalogueItemBase):
    """Schema for creating a global catalogue item."""
    pass


class GlobalCatalogueItemUpdate(BaseModel):
    """Schema for updating a global catalogue item."""
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, min_length=1, max_length=50)
    weight: float | None = Field(None, gt=0)
    weight_unit: GearWeightUnit | None = None
    description: str | None = None
    brand: str | None = Field(None, max_length=255)
    model: str | None = Field(None, max_length=255)
    price_tier: str | None = Field(None, pattern="^(low|medium|high)$")
    quality: GearItemQuality | None = None  # Użyj istniejącego typu GearItemQuality (low, medium, high)
    url: str | None = None
    color: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class GlobalCatalogueItemResponse(GlobalCatalogueItemBase):
    """Schema for global catalogue item response."""
    id: str
    version: int
    is_active: bool
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GlobalCatalogueItemSearchParams(BaseModel):
    """Schema for catalogue item search parameters."""
    query: str | None = None
    category: str | None = None
    brand: str | None = None
    price_tier: str | None = None
    quality: str | None = None
    is_active: bool | None = True
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
```

### Faza 2: Backend - Repository i Service

**Uwaga:** Trzeba zaktualizować istniejące metody `create_item` i `update_item` w repository, aby obsługiwały pole `catalogue_item_id` z schematu `ItemCreate`/`ItemUpdate`.

#### Step 2.1: Dodanie metod do Repository

**File:** `backend/app/modules/gear/repository.py`

```python
async def get_catalogue_items(
    self,
    query: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    price_tier: str | None = None,
    quality: str | None = None,
    is_active: bool | None = True,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[GlobalCatalogueItemDB]:
    """Get global catalogue items with filtering and search.

    Args:
        query: Search query (searches in name, description, brand, model)
        category: Filter by category
        brand: Filter by brand
        price_tier: Filter by price tier
        quality: Filter by quality
        is_active: Filter by active status
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of catalogue items
    """
    stmt = select(GlobalCatalogueItemDB)

    # Build filters
    conditions = []
    if is_active is not None:
        conditions.append(GlobalCatalogueItemDB.is_active == is_active)
    if category:
        conditions.append(GlobalCatalogueItemDB.category == category)
    if brand:
        conditions.append(GlobalCatalogueItemDB.brand == brand)
    if price_tier:
        conditions.append(GlobalCatalogueItemDB.price_tier == price_tier)
    if quality:
        conditions.append(GlobalCatalogueItemDB.quality == quality)

    # Search query (fuzzy search in name, description, brand, model)
    if query:
        search_pattern = f"%{query}%"
        search_conditions = or_(
            GlobalCatalogueItemDB.name.ilike(search_pattern),
            GlobalCatalogueItemDB.description.ilike(search_pattern),
            GlobalCatalogueItemDB.brand.ilike(search_pattern),
            GlobalCatalogueItemDB.model.ilike(search_pattern),
        )
        conditions.append(search_conditions)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Order by name
    stmt = stmt.order_by(GlobalCatalogueItemDB.name.asc())

    # Pagination
    stmt = stmt.offset(skip).limit(limit)

    result = await self.db.execute(stmt)
    return result.scalars().all()


async def get_catalogue_item(self, item_id: str) -> GlobalCatalogueItemDB | None:
    """Get a single catalogue item by ID.

    Args:
        item_id: Catalogue item ID

    Returns:
        Catalogue item if found, None otherwise
    """
    stmt = select(GlobalCatalogueItemDB).where(GlobalCatalogueItemDB.id == item_id)
    result = await self.db.execute(stmt)
    return result.scalar_one_or_none()


async def create_catalogue_item(
    self,
    user_id: str,
    data: GlobalCatalogueItemCreate,
) -> GlobalCatalogueItemDB:
    """Create a new catalogue item.

    Args:
        user_id: User ID creating the item
        data: Item creation data

    Returns:
        Created catalogue item
    """
    from app.common.id_utils import generate_id
    
    item_id = generate_id()
    item = GlobalCatalogueItemDB(
        id=item_id,
        version=1,
        name=data.name,
        category=data.category,
        weight=data.weight,
        weight_unit=data.weight_unit,
        description=data.description,
        brand=data.brand,
        model=data.model,
        price_tier=data.price_tier,
        quality=data.quality,
        url=data.url,
        color=data.color,
        is_active=True,
        created_by=user_id,
    )
    self.db.add(item)
    await self.db.commit()
    await self.db.refresh(item)
    return item


async def update_catalogue_item(
    self,
    item_id: str,
    user_id: str,
    data: GlobalCatalogueItemUpdate,
    is_admin: bool = False,
) -> GlobalCatalogueItemDB | None:
    """Update a catalogue item.

    Only the creator or admin can update items.

    Args:
        item_id: Catalogue item ID
        user_id: User ID updating the item
        data: Update data
        is_admin: Whether user is admin

    Returns:
        Updated item if found and user has permission, None otherwise
    """
    item = await self.get_catalogue_item(item_id)
    if not item:
        return None

    # Check permissions: creator or admin
    if not is_admin and item.created_by != user_id:
        return None

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    # Increment version on update
    item.version += 1

    await self.db.commit()
    await self.db.refresh(item)
    return item


async def delete_catalogue_item(
    self,
    item_id: str,
    user_id: str,
    is_admin: bool = False,
) -> bool:
    """Delete a catalogue item (soft delete by setting is_active=False).

    Only the creator or admin can delete items.

    Args:
        item_id: Catalogue item ID
        user_id: User ID deleting the item
        is_admin: Whether user is admin

    Returns:
        True if deleted, False otherwise
    """
    item = await self.get_catalogue_item(item_id)
    if not item:
        return False

    # Check permissions: creator or admin
    if not is_admin and item.created_by != user_id:
        return False

    # Soft delete
    item.is_active = False
    await self.db.commit()
    return True
```

#### Step 2.2: Dodanie metod do Service

**File:** `backend/app/modules/gear/service.py`

```python
async def get_catalogue_items(
    self,
    search_params: GlobalCatalogueItemSearchParams,
) -> list[GlobalCatalogueItemResponse]:
    """Get global catalogue items.

    Args:
        search_params: Search and filter parameters

    Returns:
        List of catalogue items
    """
    items = await self.repository.get_catalogue_items(
        query=search_params.query,
        category=search_params.category,
        brand=search_params.brand,
        price_tier=search_params.price_tier,
        quality=search_params.quality,
        is_active=search_params.is_active,
        skip=search_params.skip,
        limit=search_params.limit,
    )
    return [GlobalCatalogueItemResponse.model_validate(item) for item in items]


async def get_catalogue_item(self, item_id: str) -> GlobalCatalogueItemResponse | None:
    """Get a single catalogue item.

    Args:
        item_id: Catalogue item ID

    Returns:
        Catalogue item if found, None otherwise
    """
    item = await self.repository.get_catalogue_item(item_id)
    if not item:
        return None
    return GlobalCatalogueItemResponse.model_validate(item)


async def create_catalogue_item(
    self,
    user_id: str,
    data: GlobalCatalogueItemCreate,
) -> GlobalCatalogueItemResponse:
    """Create a new catalogue item.

    Args:
        user_id: User ID creating the item
        data: Item creation data

    Returns:
        Created catalogue item
    """
    item = await self.repository.create_catalogue_item(user_id, data)
    return GlobalCatalogueItemResponse.model_validate(item)


async def update_catalogue_item(
    self,
    item_id: str,
    user_id: str,
    data: GlobalCatalogueItemUpdate,
    is_admin: bool = False,
) -> GlobalCatalogueItemResponse | None:
    """Update a catalogue item.

    Args:
        item_id: Catalogue item ID
        user_id: User ID updating the item
        data: Update data
        is_admin: Whether user is admin

    Returns:
        Updated item if found and user has permission, None otherwise
    """
    item = await self.repository.update_catalogue_item(item_id, user_id, data, is_admin)
    if not item:
        return None
    return GlobalCatalogueItemResponse.model_validate(item)


async def delete_catalogue_item(
    self,
    item_id: str,
    user_id: str,
    is_admin: bool = False,
) -> bool:
    """Delete a catalogue item (soft delete).

    Args:
        item_id: Catalogue item ID
        user_id: User ID deleting the item
        is_admin: Whether user is admin

    Returns:
        True if deleted, False otherwise
    """
    return await self.repository.delete_catalogue_item(item_id, user_id, is_admin)


async def add_catalogue_item_to_container(
    self,
    container_id: str,
    catalogue_item_id: str,
    user_id: str,
    quantity: int = 1,
    status: str = "owned",
    priority: str = "medium",
) -> ItemResponse | None:
    """Add a catalogue item to a user's container.

    Creates a new item in the container based on catalogue item data.
    The new item is independent (not linked to catalogue).

    Args:
        container_id: Target container ID
        catalogue_item_id: Catalogue item ID to copy
        user_id: User ID
        quantity: Item quantity (default: 1)
        status: Item status (default: "owned")
        priority: Item priority (default: "medium")

    Returns:
        Created item if successful, None otherwise
    """
    # Get catalogue item
    catalogue_item = await self.repository.get_catalogue_item(catalogue_item_id)
    if not catalogue_item or not catalogue_item.is_active:
        return None

    # Verify container belongs to user
    container = await self.repository.get_container(container_id, user_id)
    if not container:
        return None

    # Create item from catalogue data
    item_data = ItemCreate(
        name=catalogue_item.name,
        category=catalogue_item.category,
        weight=catalogue_item.weight,
        weight_unit=catalogue_item.weight_unit,
        quantity=quantity,
        status=status,
        priority=priority,
        brand=catalogue_item.brand,
        color=catalogue_item.color,
        url=catalogue_item.url,
        # Note: We don't copy price, quality, description as these may differ
        # User can edit the item after adding it
    )

    # Create item and set catalogue_item_id
    created_item = await self.create_item(container_id, user_id, item_data)
    if created_item:
        # Update item to set catalogue_item_id
        update_data = ItemUpdate(catalogue_item_id=catalogue_item_id)
        return await self.update_item(created_item.id, user_id, update_data)
    return None


async def unlink_item_from_catalogue(
    self,
    item_id: str,
    user_id: str,
) -> ItemResponse | None:
    """Unlink an item from the catalogue (clear catalogue_item_id).

    Args:
        item_id: Item ID to unlink
        user_id: User ID (must own the item)

    Returns:
        Updated item if successful, None otherwise
    """
    item = await self.repository.get_item(item_id, user_id)
    if not item:
        return None
    
    # Clear catalogue_item_id
    update_data = ItemUpdate(catalogue_item_id=None)
    return await self.update_item(item_id, user_id, update_data)
```

### Faza 3: Backend - Router i Endpointy

#### Step 3.1: Dodanie endpointów do routera

**File:** `backend/app/modules/gear/router.py`

**Uwaga:** `OptionalUser` jest już zdefiniowany w `router.py` (linia 96), więc można go użyć bezpośrednio.

```python
from .schemas import (
    # ... existing imports
    GlobalCatalogueItemCreate,
    GlobalCatalogueItemResponse,
    GlobalCatalogueItemSearchParams,
    GlobalCatalogueItemUpdate,
)

# ... existing code
# OptionalUser is already defined in router.py (line 96)

# Global Catalogue endpoints (public - no authentication required for GET)
@router.get(
    "/catalogue/items",
    response_model=list[GlobalCatalogueItemResponse],
    summary="Get global catalogue items",
)
async def get_catalogue_items(
    query: str | None = Query(None, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    brand: str | None = Query(None, description="Filter by brand"),
    price_tier: str | None = Query(None, description="Filter by price tier"),
    quality: str | None = Query(None, description="Filter by quality"),
    is_active: bool | None = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    service: GearServiceDep = Depends(get_gear_service),
    current_user: OptionalUser = None,
) -> list[GlobalCatalogueItemResponse]:
    """Get global catalogue items with filtering and search.

    Args:
        query: Search query
        category: Filter by category
        brand: Filter by brand
        price_tier: Filter by price tier
        quality: Filter by quality
        is_active: Filter by active status
        skip: Number of records to skip
        limit: Maximum number of records to return
        service: Gear service instance
        current_user: Optional authenticated user (for future use, e.g., personalized results)

    Returns:
        List of catalogue items
    """
    search_params = GlobalCatalogueItemSearchParams(
        query=query,
        category=category,
        brand=brand,
        price_tier=price_tier,
        quality=quality,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return await service.get_catalogue_items(search_params)


@router.get(
    "/catalogue/items/{item_id}",
    response_model=GlobalCatalogueItemResponse,
    summary="Get a catalogue item by ID",
)
async def get_catalogue_item(
    item_id: str,
    service: GearServiceDep = Depends(get_gear_service),
    current_user: OptionalUser = None,
) -> GlobalCatalogueItemResponse:
    """Get a single catalogue item by ID.

    Args:
        item_id: Catalogue item ID
        service: Gear service instance
        current_user: Optional authenticated user (for future use, e.g., personalized results)

    Returns:
        Catalogue item

    Raises:
        HTTPException: If item not found
    """
    item = await service.get_catalogue_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalogue item not found",
        )
    return item


@router.post(
    "/catalogue/items",
    response_model=GlobalCatalogueItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new catalogue item",
)
async def create_catalogue_item(
    data: GlobalCatalogueItemCreate,
    current_user: CurrentUser,
    service: GearServiceDep = Depends(get_gear_service),
) -> GlobalCatalogueItemResponse:
    """Create a new catalogue item.

    Args:
        data: Item creation data
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Created catalogue item
    """
    return await service.create_catalogue_item(current_user.id, data)


@router.patch(
    "/catalogue/items/{item_id}",
    response_model=GlobalCatalogueItemResponse,
    summary="Update a catalogue item",
)
async def update_catalogue_item(
    item_id: str,
    data: GlobalCatalogueItemUpdate,
    current_user: CurrentUser,
    service: GearServiceDep = Depends(get_gear_service),
) -> GlobalCatalogueItemResponse:
    """Update a catalogue item.

    Only the creator or admin can update items.

    Args:
        item_id: Catalogue item ID
        data: Update data
        current_user: Authenticated user
        service: Gear service instance
        is_admin: Whether user is admin (optional)

    Returns:
        Updated catalogue item

    Raises:
        HTTPException: If item not found or user doesn't have permission
    """
    # Check if user is admin or creator
    # User model has isAdmin property (camelCase)
    is_admin = current_user.isAdmin
    item = await service.update_catalogue_item(
        item_id,
        current_user.id,
        data,
        is_admin=is_admin,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalogue item not found or you don't have permission to update it",
        )
    return item


@router.delete(
    "/catalogue/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a catalogue item (soft delete)",
)
async def delete_catalogue_item(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep = Depends(get_gear_service),
) -> None:
    """Delete a catalogue item (soft delete by setting is_active=False).

    Only the creator or admin can delete items.

    Args:
        item_id: Catalogue item ID
        current_user: Authenticated user
        service: Gear service instance
        is_admin: Whether user is admin (optional)

    Raises:
        HTTPException: If item not found or user doesn't have permission
    """
    # Check if user is admin or creator
    is_admin = current_user.isAdmin if hasattr(current_user, 'isAdmin') else False
    deleted = await service.delete_catalogue_item(
        item_id,
        current_user.id,
        is_admin=is_admin,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalogue item not found or you don't have permission to delete it",
        )


@router.post(
    "/containers/{container_id}/items/from-catalogue/{catalogue_item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a catalogue item to a container",
)
async def add_catalogue_item_to_container(
    container_id: str,
    catalogue_item_id: str,
    current_user: CurrentUser,
    quantity: int = Query(1, ge=1, description="Item quantity"),
    status: str = Query("owned", description="Item status"),
    priority: str = Query("medium", description="Item priority"),
    service: GearServiceDep = Depends(get_gear_service),
) -> ItemResponse:
    """Add a catalogue item to a user's container.

    Creates a new item in the container based on catalogue item data.
    The new item is independent (not linked to catalogue).

    Args:
        container_id: Target container ID
        catalogue_item_id: Catalogue item ID to copy
        current_user: Authenticated user
        quantity: Item quantity
        status: Item status
        priority: Item priority
        service: Gear service instance

    Returns:
        Created item

    Raises:
        HTTPException: If container or catalogue item not found
    """
    item = await service.add_catalogue_item_to_container(
        container_id,
        catalogue_item_id,
        current_user.id,
        quantity=quantity,
        status=status,
        priority=priority,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container or catalogue item not found",
        )
    return item


@router.patch(
    "/items/{item_id}/unlink-from-catalogue",
    response_model=ItemResponse,
    summary="Unlink item from catalogue",
)
async def unlink_item_from_catalogue(
    item_id: str,
    current_user: CurrentUser,
    service: GearServiceDep = Depends(get_gear_service),
) -> ItemResponse:
    """Unlink an item from the catalogue (clear catalogue_item_id).

    Args:
        item_id: Item ID to unlink
        current_user: Authenticated user
        service: Gear service instance

    Returns:
        Updated item

    Raises:
        HTTPException: If item not found or user doesn't own it
    """
    item = await service.unlink_item_from_catalogue(item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you don't have permission to modify it",
        )
    return item
```

#### Step 3.2: Endpointy do zarządzania obrazkami katalogu

**File:** `backend/app/modules/gear/catalogue_item_image_router.py`

**Uwaga:** Endpointy identyczne jak `item_image_router.py`, ale dla przedmiotów katalogu. Wymagają autoryzacji (nie są publiczne) - tylko admini mogą uploadować/usuwać obrazki.

```python
"""FastAPI router for catalogue item image endpoints.

Endpoints for uploading and managing images for global catalogue items.
Requires authentication (not public) to prevent unauthorized S3 costs.
Only admins can upload/delete images.
"""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import AdminUser
from app.modules.gear.image_upload_service import ImageUploadService
from app.modules.gear.catalogue_item_image_repository import CatalogueItemImageRepository

router = APIRouter(prefix="/gear/catalogue/items", tags=["catalogue-images"])


def get_catalogue_image_repository(db: AsyncSession = Depends(get_db)) -> CatalogueItemImageRepository:
    """Dependency to get catalogue image repository instance."""
    return CatalogueItemImageRepository(db)


def get_catalogue_image_service(
    repository: CatalogueItemImageRepository = Depends(get_catalogue_image_repository),
) -> ImageUploadService:
    """Dependency to get catalogue image service instance."""
    return ImageUploadService(repository)


@router.post(
    "/{item_id}/images",
    summary="Upload image for catalogue item",
    status_code=status.HTTP_201_CREATED,
)
async def upload_catalogue_item_image(
    item_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Query(False, description="Whether this should be the primary image"),
    current_user: AdminUser = None,  # Only admins can upload catalogue images
    service: ImageUploadService = Depends(get_catalogue_image_service),
) -> dict:
    """Upload an image for a catalogue item.

    Args:
        item_id: Catalogue item ID
        file: Image file to upload
        is_primary: Whether this should be the primary image
        current_user: Authenticated admin user
        service: Image upload service instance

    Returns:
        Image data with URL

    Raises:
        HTTPException: If upload fails or user is not admin
    """
    result = await service.upload_image(
        item_id=item_id,
        file=file,
        user_id=current_user.id,
        is_primary=is_primary,
    )
    return result


@router.get(
    "/{item_id}/images",
    summary="Get all images for catalogue item",
)
async def get_catalogue_item_images(
    item_id: str,
    service: ImageUploadService = Depends(get_catalogue_image_service),
) -> list[dict]:
    """Get all images for a catalogue item.

    Args:
        item_id: Catalogue item ID
        service: Image upload service instance

    Returns:
        List of image data with URLs
    """
    return await service.get_item_images(item_id)


@router.delete(
    "/{item_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete catalogue item image",
)
async def delete_catalogue_item_image(
    item_id: str,
    image_id: str,
    current_user: AdminUser = None,  # Only admins can delete catalogue images
    service: ImageUploadService = Depends(get_catalogue_image_service),
) -> None:
    """Delete an image for a catalogue item.

    Args:
        item_id: Catalogue item ID
        image_id: Image ID to delete
        current_user: Authenticated admin user
        service: Image upload service instance

    Raises:
        HTTPException: If deletion fails or user is not admin
    """
    deleted = await service.delete_image(image_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found or you don't have permission to delete it",
        )


@router.patch(
    "/{item_id}/images/{image_id}/set-primary",
    summary="Set primary image for catalogue item",
)
async def set_catalogue_item_primary_image(
    item_id: str,
    image_id: str,
    current_user: AdminUser = None,  # Only admins can set primary image
    service: ImageUploadService = Depends(get_catalogue_image_service),
) -> dict:
    """Set primary image for a catalogue item.

    Args:
        item_id: Catalogue item ID
        image_id: Image ID to set as primary
        current_user: Authenticated admin user
        service: Image upload service instance

    Returns:
        Success message

    Raises:
        HTTPException: If operation fails or user is not admin
    """
    success = await service.set_primary_image(item_id, image_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found or you don't have permission to modify it",
        )
    return {"message": "Primary image updated"}
```

**Uwaga:** Trzeba dodać `router.include_router(catalogue_item_image_router)` w głównym routerze gear (`router.py`).

### Faza 4: Backend - Seed Data (Opcjonalnie)

#### Step 4.1: Skrypt do importu danych z global-catalogue-items.md

**File:** `backend/scripts/seed_catalogue_items.py`

```python
"""Script to seed global catalogue items from markdown file."""
import asyncio
from pathlib import Path

from app.core.database import get_db
from app.modules.gear.repository import GearRepository
from app.modules.gear.schemas import GlobalCatalogueItemCreate

# Parse markdown file and create items
# Implementation depends on markdown format
```

### Faza 5: Frontend - Typy i API Client

#### Step 5.1: Dodanie typów TypeScript

**File:** `src/modules/gear/types/gear.types.ts`

```typescript
// Global Catalogue Item
export interface IGlobalCatalogueItem {
  id: TUUID
  version: number
  name: string
  category: TGearItemCategory
  weight: number
  weightUnit: TGearWeightUnit
  description?: string | null
  brand?: string | null
  model?: string | null
  priceTier?: 'low' | 'medium' | 'high' | null  // Nowe pole - nie istnieje w IGearItem
  quality?: TGearItemQuality | null  // Zgodne z IGearItem (low, medium, high)
  url?: string | null
  color?: string | null
  isActive: boolean
  createdBy?: TUUID | null
  createdAt: TDateTime
  updatedAt: TDateTime
}

export interface IGlobalCatalogueItemSearchParams {
  query?: string | null
  category?: string | null
  brand?: string | null
  priceTier?: 'low' | 'medium' | 'high' | null
  quality?: TGearItemQuality | null
  isActive?: boolean | null
  skip?: number
  limit?: number
}

// Update IGearItem interface to include catalogueItemId
// Add to existing IGearItem interface in gear.types.ts:
// catalogueItemId?: TUUID | null // Reference to global catalogue item (if added from catalogue)
```

#### Step 5.2: Dodanie metod do API Client

**File:** `src/shared/services/apiClient.ts` lub nowy plik `src/modules/gear/services/gearCatalogueApiService.ts`

```typescript
import { apiClient } from '@/shared/services/apiClient'
import type { IGlobalCatalogueItem, IGlobalCatalogueItemSearchParams } from '@/modules/gear/types/gear.types'

export async function getCatalogueItems(
  params: IGlobalCatalogueItemSearchParams = {},
): Promise<IGlobalCatalogueItem[]> {
  const response = await apiClient.get<IGlobalCatalogueItem[]>('/gear/catalogue/items', { params })
  return response.data
}

export async function getCatalogueItem(itemId: TUUID): Promise<IGlobalCatalogueItem> {
  const response = await apiClient.get<IGlobalCatalogueItem>(`/gear/catalogue/items/${itemId}`)
  return response.data
}

export async function addCatalogueItemToContainer(
  containerId: TUUID,
  catalogueItemId: TUUID,
  quantity: number = 1,
  status: TGearItemStatus = 'owned',
  priority: TGearItemPriority = 'medium',
): Promise<IGearItem> {
  const response = await apiClient.post<IGearItem>(
    `/gear/containers/${containerId}/items/from-catalogue/${catalogueItemId}`,
    null,
    {
      params: { quantity, status, priority },
    },
  )
  return response.data
}

export async function unlinkItemFromCatalogue(itemId: TUUID): Promise<IGearItem> {
  const response = await apiClient.patch<IGearItem>(`/gear/items/${itemId}/unlink-from-catalogue`)
  return response.data
}
```

### Faza 6: Frontend - Przeglądarka Katalogu

**Uwaga:** Użyj async components (`defineAsyncComponent`) dla optymalizacji - komponenty katalogu nie muszą być ładowane od razu.

#### Step 6.1: Strona przeglądarki katalogu

**File:** `src/modules/gear/pages/CatalogueBrowserPage.vue`

**Uwaga:** Strona publiczna (dostępna bez logowania). Użyj `DataTable` z server-side paginacją.

- Lista przedmiotów z katalogu (użyj `DataTable` z paginacją)
- Filtry: kategoria, brand, price tier, quality
- Wyszukiwarka (query)
- Karty przedmiotów z podstawowymi informacjami
- Przycisk "Dodaj do kontenera" (otwiera dialog wyboru kontenera - tylko dla zalogowanych)
- Server-side paginacja (użyj `skip`/`limit` z API)
- Link do strony szczegółów przedmiotu (`/catalogue/items/:id`)

**Optymalizacja:** Użyj `defineAsyncComponent` dla cięższych komponentów (np. `CatalogueItemCard`).

#### Step 6.2: Komponent karty przedmiotu katalogu

**File:** `src/modules/gear/components/CatalogueItemCard.vue`

- Wyświetlanie podstawowych informacji (nazwa, kategoria, brand, waga)
- Badge z price tier i quality
- Obrazek przedmiotu (jeśli dostępny)
- Przycisk "Dodaj do kontenera" (tylko dla zalogowanych)
- Link do strony szczegółów przedmiotu

**Optymalizacja:** Użyj `defineAsyncComponent` jeśli komponent jest duży.

#### Step 6.3: Strona szczegółów przedmiotu w katalogu

**File:** `src/modules/gear/pages/CatalogueItemDetailPage.vue`

**Uwaga:** Strona publiczna (dostępna bez logowania). Galeria obrazków dla zalogowanych, readonly + info dla niezalogowanych.

- Wyświetlanie pełnych informacji o przedmiocie z katalogu
- Galeria obrazków:
  - Dla zalogowanych: pełna galeria (jeśli admin - możliwość uploadu)
  - Dla niezalogowanych: readonly + info "Zaloguj się aby zobaczyć więcej"
- Przycisk "Dodaj do kontenera" (otwiera dialog wyboru kontenera - tylko dla zalogowanych)
- Link do produktu (jeśli dostępny)
- Badge z price tier i quality

**Route:** `/catalogue/items/:id` (publiczny)

**Optymalizacja:** Użyj `defineAsyncComponent` dla galerii obrazków.

#### Step 6.4: Dialog wyboru kontenera

**File:** `src/modules/gear/components/AddCatalogueItemToContainerDialog.vue`

**Uwaga:** Dialog z ComboBox do wyboru kontenera. Podobny do `AddNestedContainerDialog.vue`, ale używa ComboBox z wyszukiwaniem.

- ComboBox z wyszukiwaniem kontenerów użytkownika (podobny do `ItemCatalogSelector.vue`)
- Używa `useGear()` do pobrania kontenerów użytkownika
- Po wyborze kontenera → wywołanie `addCatalogueItemToContainer()`
- Toast po dodaniu (bez przekierowania)
- Zamykanie dialogu po dodaniu

**Użycie:**
- Z `CatalogueBrowserPage.vue` (przycisk "Dodaj do kontenera")
- Z `CatalogueItemDetailPage.vue` (przycisk "Dodaj do kontenera")

### Faza 7: Frontend - Autocomplete z Katalogiem

#### Step 7.1: Rozszerzenie ItemFormPage

**File:** `src/modules/gear/pages/ItemFormPage.vue`

**Uwaga:** ItemFormPage już ma tabs z "new" i "catalog" (przedmioty użytkownika). Trzeba dodać trzeci tab.

- Zmień typ `tabMode` z `'new' | 'catalog'` na `'new' | 'catalog' | 'globalCatalogue'`
- Dodaj trzeci `TabsTrigger` z wartością `"globalCatalogue"` i etykietą "From Global Catalogue"
- Dodaj `TabsContent` dla `"globalCatalogue"` z komponentem `GlobalCatalogueSelector`
- Autocomplete z globalnym katalogiem (podobnie jak z przedmiotami użytkownika)
- Po wyborze przedmiotu z katalogu - pre-fill formularza
- **Ważne:** Ustawiamy `catalogueItemId` przy tworzeniu przedmiotu (nie `linkedItemId`)
- Przedmiot z katalogu jest kopiowany, ale zachowuje referencję do katalogu

#### Step 7.2: Komponent GlobalCatalogueSelector

**File:** `src/modules/gear/components/GlobalCatalogueSelector.vue`

- Podobny do `ItemCatalogSelector.vue`, ale używa API do pobierania przedmiotów z globalnego katalogu
- Używa `useCatalogue()` composable do pobierania danych
- Wyświetla przedmioty z katalogu z podstawowymi informacjami (nazwa, kategoria, brand)

#### Step 7.3: Composable do zarządzania katalogiem

**File:** `src/modules/gear/composables/useCatalogue.ts`

```typescript
export function useCatalogue() {
  const { data: items, isLoading, refetch } = useQuery({
    queryKey: ['catalogue', 'items'],
    queryFn: () => getCatalogueItems({ isActive: true }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const searchItems = async (params: IGlobalCatalogueItemSearchParams) => {
    return await getCatalogueItems(params)
  }

  const addToContainer = async (
    containerId: TUUID,
    catalogueItemId: TUUID,
    quantity: number = 1,
    status: TGearItemStatus = 'owned',
    priority: TGearItemPriority = 'medium',
  ) => {
    return await addCatalogueItemToContainer(containerId, catalogueItemId, quantity, status, priority)
  }

  return {
    items,
    isLoading,
    refetch,
    searchItems,
    addToContainer,
  }
}
```

### Faza 8: Frontend - Badge z linkiem do katalogu

#### Step 8.1: Dodanie badge w ItemHeader

**File:** `src/modules/gear/components/ItemHeader.vue`

- Dodaj badge "Z katalogu" + ikona książki (tylko gdy `item.catalogueItemId` istnieje)
- Badge jako link do `/catalogue/items/{catalogueItemId}`
- Użyj `RouterLink` z `GearRoutePath.CatalogueItemDetailById(catalogueItemId)`

#### Step 8.2: Dodanie akcji "Odepnij od katalogu" w dropdown menu

**File:** `src/modules/gear/components/ItemsTableRowActions.vue` lub podobny komponent

- Dodaj akcję "Odepnij od katalogu" w dropdown menu (tylko gdy `item.catalogueItemId` istnieje)
- Wywołanie `unlinkItemFromCatalogue(itemId)`
- Toast po odpięciu
- Odświeżenie danych

**Uwaga:** Można też dodać tę akcję w `ItemDetailPage.vue` jeśli ma dropdown menu.

### Faza 9: Frontend - Zarządzanie Katalogiem (Admin)

#### Step 9.1: Strona zarządzania katalogiem

**File:** `src/modules/gear/pages/CatalogueManagementPage.vue` (tylko dla adminów)

**Uwaga:** Na razie nie implementujemy CRUD - będzie później.

- Lista wszystkich przedmiotów katalogu
- Formularz dodawania/edycji przedmiotu
- Możliwość deaktywacji przedmiotów
- Import z markdown (opcjonalnie)

## 🔄 Wersjonowanie

**Koncepcja:**
- Każdy przedmiot w katalogu ma pole `version`
- Przy aktualizacji przedmiotu, `version` jest inkrementowane
- Użytkownicy mogą widzieć, która wersja przedmiotu została użyta (opcjonalnie w przyszłości)

**Implementacja:**
- Pole `version` w modelu (już dodane)
- Automatyczna inkrementacja przy update (już w repository)

## 📊 Migracja Danych

**Import z global-catalogue-items.md:**
- Skrypt parsujący markdown
- Tworzenie przedmiotów w katalogu
- Mapowanie pól:
  - `kategoria` → `category`
  - `firma` → `brand`
  - `model` → `model`
  - `opis` → `description`
  - `półka cenowa` → `price_tier` (low/medium/high)
  - `klasa` → `quality` (mapowanie: basic/value → low, solid/reliable → medium, durable/premium → high)
  - `website` → `url`
  
**Uwaga:** W pliku `global-catalogue-items.md` są klasy: basic, value, solid, reliable, durable, premium. 
W bazie używamy `GearItemQuality` (low, medium, high), więc trzeba zmapować:
- basic, value → low
- solid, reliable → medium  
- durable, premium → high

## 🧪 Testy

### Backend
- Testy repository (get, create, update, delete)
- Testy service
- Testy endpointów API
- Testy uprawnień (tylko creator/admin może edytować)

### Frontend
- Testy composable `useCatalogue`
- Testy komponentów (CatalogueBrowserPage, CatalogueItemCard)
- Testy integracji z ItemFormPage

## 📝 Notatki

- **Linkowanie vs Katalog:** Globalny katalog to źródło szablonów, nie jest linkowane z przedmiotami użytkownika. Linkowanie działa tylko między przedmiotami użytkownika w różnych kontenerach.
- **Niezależność:** Przedmioty dodane z katalogu są niezależne - użytkownik może je swobodnie edytować. Pole `catalogueItemId` pozwala śledzić pochodzenie, ale nie wpływa na edycję.
- **Wersjonowanie:** Pole `version` pozwala na śledzenie zmian w katalogu, ale nie wpływa na już dodane przedmioty użytkownika.
- **Obrazki katalogu:** Obrazki katalogu wymagają autoryzacji (nie są publiczne) - tylko admini mogą uploadować/usuwać, aby uniknąć nieautoryzowanych kosztów S3.
- **Odepinanie od katalogu:** Użytkownik może odpiąć przedmiot od katalogu (akcja "Odepnij od katalogu"), co czyści pole `catalogueItemId`. Po odpięciu przedmiot pozostaje niezależny.

## ⚡ Optymalizacja - Async Components

**Zalecenia dotyczące użycia `defineAsyncComponent`:**

1. **CatalogueBrowserPage.vue** - użyj async dla:
   - `CatalogueItemCard.vue` (jeśli duży)
   - `AddCatalogueItemToContainerDialog.vue`

2. **CatalogueItemDetailPage.vue** - użyj async dla:
   - Galeria obrazków (jeśli duża)
   - `AddCatalogueItemToContainerDialog.vue`

3. **ItemFormPage.vue** - użyj async dla:
   - `GlobalCatalogueSelector.vue` (jeśli duży)

**Przykład użycia:**
```typescript
const CatalogueItemCard = defineAsyncComponent(() => import('../components/CatalogueItemCard.vue'))
```

**Korzyści:**
- Mniejsze początkowe bundle size
- Szybsze ładowanie strony
- Lepsze UX (komponenty ładowane na żądanie)

## ✅ Weryfikacja i Poprawki

**Data weryfikacji:** 2025-01-21

### Wprowadzone poprawki:

1. **Błąd wcięcia w modelu** (linie 104-105)
   - Poprawiono wcięcie dla pól `price_tier` i `quality` w `GlobalCatalogueItemDB`

2. **Funkcja generowania ID**
   - Zmieniono `generate_ulid()` na `generate_id()` z `app.common.id_utils`
   - Dodano import w metodzie `create_catalogue_item` w repository

3. **Publiczne endpointy GET**
   - Dodano parametr `current_user: OptionalUser = None` do:
     - `get_catalogue_items()` - endpoint przeglądania katalogu
     - `get_catalogue_item()` - endpoint pobierania pojedynczego przedmiotu
   - Endpointy GET są publiczne (nie wymagają autoryzacji)
   - `OptionalUser` jest już zdefiniowany w `router.py` (linia 96)

4. **Dokumentacja endpointów**
   - Zaktualizowano dokumentację endpointów GET z informacją o opcjonalnym użytkowniku

### Zgodność z istniejącym kodem:

- ✅ Typy zgodne z istniejącymi (`GearItemQuality`, `GearWeightUnit`)
- ✅ Użycie `CurrentUser` jako parametr funkcji (zgodnie z regułami projektu)
- ✅ Format migracji zgodny z istniejącymi migracjami (async z `text()`)
- ✅ Schematy Pydantic zgodne z konwencjami projektu (camelCase w JSON)
- ✅ Endpointy POST/PATCH/DELETE wymagają autoryzacji (`CurrentUser`)

### Dodatkowe elementy dodane podczas weryfikacji:

5. **Obrazki katalogu**
   - Model `CatalogueItemImageDB` (identyczny z `ItemImageDB`)
   - Migracja dla tabeli `catalogue_item_images`
   - Endpointy `/gear/catalogue/items/{id}/images` (wymagają autoryzacji - tylko admini)
   - Galeria obrazków na stronie szczegółów katalogu (dla zalogowanych: pełna, dla niezalogowanych: readonly + info)

6. **Pole `catalogueItemId` w przedmiotach**
   - Migracja dodająca kolumnę `catalogue_item_id` do `gear_items`
   - Aktualizacja schematów Pydantic (`ItemCreate`, `ItemUpdate`, `ItemResponse`)
   - Aktualizacja typów TypeScript (`IGearItem`)
   - Endpoint do odpinania: `PATCH /gear/items/{id}/unlink-from-catalogue`

7. **Badge z linkiem do katalogu**
   - Badge "Z katalogu" + ikona książki w `ItemHeader.vue`
   - Link do `/catalogue/items/{catalogueItemId}`
   - Akcja "Odepnij od katalogu" w dropdown menu

8. **Dialog wyboru kontenera**
   - Komponent `AddCatalogueItemToContainerDialog.vue`
   - ComboBox z wyszukiwaniem kontenerów
   - Użycie z przeglądarki i strony szczegółów katalogu

9. **Strona szczegółów przedmiotu w katalogu**
   - `CatalogueItemDetailPage.vue` (publiczna)
   - Galeria obrazków (dla zalogowanych: pełna, dla niezalogowanych: readonly)
   - Przycisk "Dodaj do kontenera"

10. **Optymalizacja - Async Components**
    - Zalecenia dotyczące użycia `defineAsyncComponent` dla cięższych komponentów
    - Mniejsze bundle size i szybsze ładowanie

