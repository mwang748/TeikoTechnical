-- columns include project, subject, condition, age/sex, treatment, response, sample/sample_tyoe, time_from_treatment, various cells

-- want a subjects table to list all of the subjects' info (prj, age, condition, sex, treatment, response)
-- each subject can have multiple samples: samples -> subjects =  many -> one
-- samples table with the sample, sample type, time from treatment, subject (foreign key to subjects table), cell info

CREATE TABLE IF NOT EXISTS subjects (
    subject TEXT PRIMARY KEY,
    project TEXT,
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT
);

CREATE TABLE IF NOT EXISTS samples (
    sample TEXT PRIMARY KEY,
    subject TEXT,
    sample_type TEXT,
    time_from_treatment_start INTEGER,
    b_cell INTEGER,
    cd8_t_cell INTEGER,
    cd4_t_cell INTEGER,
    nk_cell INTEGER,
    monocyte INTEGER,
    FOREIGN KEY (subject) references subjects(subject)
);
