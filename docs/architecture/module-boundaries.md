# Module Boundaries & Team Domain Ownership

Chronon is partitioned into 4 distinct, parallel-workable domains:

```mermaid
graph LR
    subgraph Pranav["Pranav (Branch: pranav)"]
        AL["Academic Lifecycle"]
        ORCH["Generation Orchestration"]
        VER["Timetable Versioning"]
    end

    subgraph Ujwal["Ujwal (Branch: ujwal)"]
        OCR["VTU OCR & Ingestion"]
        CAT["Curriculum & Subjects"]
        FAC["Faculty & Workload"]
    end

    subgraph Pruthvik["Pruthvik (Branch: pruthvik)"]
        CPSAT["OR-Tools CP-SAT Engine"]
        CONS["Hard & Soft Constraints"]
        VAL["Independent Validator"]
    end

    subgraph Nivish["Nivish (Branch: nivish)"]
        RES["Rooms & Capacities"]
        LAB["Lab Resource Mapping"]
        SEC["Sections & Batches"]
        GRID["Timetable Grid UI"]
    end

    AL --> ORCH
    CAT --> ORCH
    FAC --> ORCH
    RES --> ORCH
    SEC --> ORCH
    ORCH -->|SchedulingInput| CPSAT
    CPSAT -->|TimetableSession[]| VAL
    VAL -->|ValidationResult| VER
    VER --> GRID
```

## Shared Data Contracts
All four domains communicate across strictly typed boundaries using Pydantic contracts:
1. `SchedulingInput`: Complete immutable payload given to solver.
2. `TimetableSession`: Generated individual class/lab period assignment.
3. `GenerationRun`: Execution metadata, solver timing, and outcome status.
4. `TimetableVersion`: Published or draft snapshot for historical auditing.
5. `ValidationResult` / `ValidationError`: Independent diagnostic report.
