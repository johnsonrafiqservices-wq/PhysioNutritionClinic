"""
Django management command to populate laboratory tests with full profiles and parameters.
Usage:
    python manage.py populate_lab_tests          # create/update only
    python manage.py populate_lab_tests --clear  # wipe all first, then create
"""

from django.core.management.base import BaseCommand
from laboratory.models import (
    LabTest, TestProfile, TestParameter, TestProfileParameter,
    LabTestResult, ParameterResult, LabTestRequest,
)


# ---------------------------------------------------------------------------
# Master data: each entry creates one LabTest + one TestProfile + N parameters
# ---------------------------------------------------------------------------
TESTS = [
    # â”€â”€ HEMATOLOGY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        'name': 'Complete Blood Count (CBC)',
        'code': 'CBC',
        'category': 'hematology',
        'sample_type': 'Blood (EDTA)',
        'price': 25000,
        'duration_hours': 4,
        'description': 'Full blood count with differential white cell count.',
        'parameters': [
            {'name': 'White Blood Cells (WBC)',       'code': 'WBC',   'unit': 'x10\u2079/L',  'result_type': 'numeric',    'ref_min': 4.0,   'ref_max': 11.0,  'critical_low': 2.0,  'critical_high': 30.0},
            {'name': 'Red Blood Cells (RBC)',          'code': 'RBC',   'unit': 'x10\u00b9\u00b2/L', 'result_type': 'numeric', 'ref_min': 4.2,  'ref_max': 5.5,   'critical_low': 2.5,  'critical_high': 7.0},
            {'name': 'Haemoglobin (Hb)',               'code': 'HGB',   'unit': 'g/dL',          'result_type': 'numeric',    'ref_min': 12.0,  'ref_max': 17.0,  'critical_low': 7.0,  'critical_high': 20.0},
            {'name': 'Haematocrit (HCT)',              'code': 'HCT',   'unit': '%',             'result_type': 'percentage', 'ref_min': 36.0,  'ref_max': 50.0,  'critical_low': 21.0, 'critical_high': 60.0},
            {'name': 'Mean Corpuscular Volume (MCV)',  'code': 'MCV',   'unit': 'fL',            'result_type': 'numeric',    'ref_min': 80.0,  'ref_max': 100.0},
            {'name': 'Mean Corpuscular Haemoglobin (MCH)', 'code': 'MCH', 'unit': 'pg',         'result_type': 'numeric',    'ref_min': 27.0,  'ref_max': 33.0},
            {'name': 'MCHC',                           'code': 'MCHC',  'unit': 'g/dL',          'result_type': 'numeric',    'ref_min': 31.5,  'ref_max': 35.7},
            {'name': 'Platelets (PLT)',                'code': 'PLT',   'unit': 'x10\u2079/L',  'result_type': 'numeric',    'ref_min': 150.0, 'ref_max': 400.0, 'critical_low': 50.0, 'critical_high': 1000.0},
            {'name': 'Neutrophils',                    'code': 'NEUT',  'unit': '%',             'result_type': 'percentage', 'ref_min': 40.0,  'ref_max': 70.0},
            {'name': 'Lymphocytes',                    'code': 'LYMPH', 'unit': '%',             'result_type': 'percentage', 'ref_min': 20.0,  'ref_max': 40.0},
            {'name': 'Monocytes',                      'code': 'MONO',  'unit': '%',             'result_type': 'percentage', 'ref_min': 2.0,   'ref_max': 8.0},
            {'name': 'Eosinophils',                    'code': 'EOS',   'unit': '%',             'result_type': 'percentage', 'ref_min': 1.0,   'ref_max': 4.0},
            {'name': 'Basophils',                      'code': 'BASO',  'unit': '%',             'result_type': 'percentage', 'ref_min': 0.0,   'ref_max': 1.0},
        ],
    },
    {
        'name': 'Erythrocyte Sedimentation Rate (ESR)',
        'code': 'ESR',
        'category': 'hematology',
        'sample_type': 'Blood (EDTA)',
        'price': 15000,
        'duration_hours': 2,
        'description': 'Measures the rate at which red cells settle â€” inflammation marker.',
        'parameters': [
            {'name': 'ESR', 'code': 'ESR-V', 'unit': 'mm/hr', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 20.0},
        ],
    },
    {
        'name': 'Blood Group & Rh Typing',
        'code': 'BLOOD-GROUP',
        'category': 'hematology',
        'sample_type': 'Blood (EDTA)',
        'price': 20000,
        'duration_hours': 2,
        'description': 'ABO and Rh blood group determination.',
        'parameters': [
            {'name': 'ABO Blood Group',  'code': 'ABO',  'unit': '', 'result_type': 'text', 'ref_text': 'A / B / AB / O', 'flag_criteria': 'none'},
            {'name': 'Rh Factor',        'code': 'RH',   'unit': '', 'result_type': 'normal_abnormal', 'ref_text': 'Positive or Negative', 'flag_criteria': 'none'},
        ],
    },
    {
        'name': 'Prothrombin Time (PT/INR)',
        'code': 'PT-INR',
        'category': 'hematology',
        'sample_type': 'Blood (Citrate)',
        'price': 30000,
        'duration_hours': 4,
        'description': 'Blood clotting assessment.',
        'parameters': [
            {'name': 'Prothrombin Time (PT)', 'code': 'PT',  'unit': 'seconds', 'result_type': 'numeric', 'ref_min': 11.0, 'ref_max': 13.5, 'critical_high': 30.0},
            {'name': 'INR',                   'code': 'INR', 'unit': '',         'result_type': 'ratio',   'ref_min': 0.8,  'ref_max': 1.2,  'critical_high': 3.0},
        ],
    },

    # â”€â”€ BIOCHEMISTRY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        'name': 'Fasting Blood Sugar (FBS)',
        'code': 'FBS',
        'category': 'biochemistry',
        'sample_type': 'Blood (Fluoride)',
        'price': 10000,
        'duration_hours': 2,
        'description': 'Fasting plasma glucose â€” diabetes screening.',
        'parameters': [
            {'name': 'Fasting Blood Glucose', 'code': 'FBG', 'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 70.0, 'ref_max': 100.0, 'critical_low': 50.0, 'critical_high': 500.0},
        ],
    },
    {
        'name': 'Random Blood Sugar (RBS)',
        'code': 'RBS',
        'category': 'biochemistry',
        'sample_type': 'Blood (Fluoride)',
        'price': 8000,
        'duration_hours': 1,
        'description': 'Random plasma glucose level.',
        'parameters': [
            {'name': 'Random Blood Glucose', 'code': 'RBG', 'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 70.0, 'ref_max': 140.0, 'critical_low': 50.0, 'critical_high': 500.0},
        ],
    },
    {
        'name': 'HbA1c (Glycated Haemoglobin)',
        'code': 'HBA1C',
        'category': 'biochemistry',
        'sample_type': 'Blood (EDTA)',
        'price': 40000,
        'duration_hours': 24,
        'description': 'Average blood glucose over 3 months.',
        'parameters': [
            {'name': 'HbA1c', 'code': 'HBA1C-V', 'unit': '%', 'result_type': 'percentage',
             'ref_text': 'Normal <5.7% | Pre-diabetic 5.7\u20136.4% | Diabetic \u22656.5%',
             'flag_criteria': 'range', 'ref_min': 0.0, 'ref_max': 5.6},
            {'name': 'Estimated Avg Glucose (eAG)', 'code': 'EAG', 'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 70.0, 'ref_max': 126.0},
        ],
    },
    {
        'name': 'Lipid Profile',
        'code': 'LIPID',
        'category': 'biochemistry',
        'sample_type': 'Blood (Serum) â€” fasting',
        'price': 35000,
        'duration_hours': 24,
        'description': 'Cholesterol and triglycerides panel.',
        'parameters': [
            {'name': 'Total Cholesterol',   'code': 'TC',   'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 200.0},
            {'name': 'LDL Cholesterol',     'code': 'LDL',  'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 130.0},
            {'name': 'HDL Cholesterol',     'code': 'HDL',  'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 40.0, 'ref_max': 999.0},
            {'name': 'Triglycerides',       'code': 'TRIG', 'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 150.0},
            {'name': 'VLDL Cholesterol',    'code': 'VLDL', 'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 5.0, 'ref_max': 40.0},
            {'name': 'LDL/HDL Ratio',       'code': 'LH-RATIO', 'unit': '', 'result_type': 'ratio',    'ref_min': 0.0, 'ref_max': 3.5},
        ],
    },
    {
        'name': 'Kidney Function Test (KFT)',
        'code': 'KFT',
        'category': 'biochemistry',
        'sample_type': 'Blood (Serum)',
        'price': 45000,
        'duration_hours': 24,
        'description': 'Renal function panel.',
        'parameters': [
            {'name': 'Serum Creatinine',   'code': 'CREAT',  'unit': 'mg/dL',         'result_type': 'numeric', 'ref_min': 0.6,  'ref_max': 1.2,  'critical_high': 10.0},
            {'name': 'Blood Urea Nitrogen (BUN)', 'code': 'BUN',  'unit': 'mg/dL',    'result_type': 'numeric', 'ref_min': 7.0,  'ref_max': 20.0, 'critical_high': 100.0},
            {'name': 'Serum Urea',         'code': 'UREA',   'unit': 'mg/dL',         'result_type': 'numeric', 'ref_min': 15.0, 'ref_max': 40.0},
            {'name': 'Uric Acid',          'code': 'UA',     'unit': 'mg/dL',         'result_type': 'numeric', 'ref_min': 2.4,  'ref_max': 7.0},
            {'name': 'eGFR',               'code': 'EGFR',   'unit': 'mL/min/1.73m\u00b2', 'result_type': 'numeric', 'ref_min': 60.0, 'ref_max': 999.0},
        ],
    },
    {
        'name': 'Liver Function Test (LFT)',
        'code': 'LFT',
        'category': 'biochemistry',
        'sample_type': 'Blood (Serum)',
        'price': 50000,
        'duration_hours': 24,
        'description': 'Hepatic function panel.',
        'parameters': [
            {'name': 'Total Bilirubin',    'code': 'TBIL',   'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 0.3,  'ref_max': 1.2},
            {'name': 'Direct Bilirubin',   'code': 'DBIL',   'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 0.0,  'ref_max': 0.3},
            {'name': 'Indirect Bilirubin', 'code': 'IBIL',   'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 0.2,  'ref_max': 0.9},
            {'name': 'ALT (SGPT)',         'code': 'ALT',    'unit': 'U/L',   'result_type': 'numeric', 'ref_min': 7.0,  'ref_max': 56.0,  'critical_high': 1000.0},
            {'name': 'AST (SGOT)',         'code': 'AST',    'unit': 'U/L',   'result_type': 'numeric', 'ref_min': 10.0, 'ref_max': 40.0,  'critical_high': 1000.0},
            {'name': 'Alkaline Phosphatase (ALP)', 'code': 'ALP', 'unit': 'U/L', 'result_type': 'numeric', 'ref_min': 44.0, 'ref_max': 147.0},
            {'name': 'GGT',               'code': 'GGT',    'unit': 'U/L',   'result_type': 'numeric', 'ref_min': 9.0,  'ref_max': 48.0},
            {'name': 'Total Protein',      'code': 'TPROT',  'unit': 'g/dL',  'result_type': 'numeric', 'ref_min': 6.3,  'ref_max': 8.2},
            {'name': 'Albumin',            'code': 'ALB',    'unit': 'g/dL',  'result_type': 'numeric', 'ref_min': 3.5,  'ref_max': 5.0},
            {'name': 'Globulin',           'code': 'GLOB',   'unit': 'g/dL',  'result_type': 'numeric', 'ref_min': 2.0,  'ref_max': 3.5},
        ],
    },
    {
        'name': 'Serum Electrolytes',
        'code': 'ELECTROLYTES',
        'category': 'biochemistry',
        'sample_type': 'Blood (Serum)',
        'price': 35000,
        'duration_hours': 24,
        'description': 'Sodium, potassium, chloride and bicarbonate levels.',
        'parameters': [
            {'name': 'Sodium (Na\u207a)',     'code': 'NA',  'unit': 'mmol/L', 'result_type': 'numeric', 'ref_min': 135.0, 'ref_max': 145.0, 'critical_low': 120.0, 'critical_high': 160.0},
            {'name': 'Potassium (K\u207a)',   'code': 'K',   'unit': 'mmol/L', 'result_type': 'numeric', 'ref_min': 3.5,   'ref_max': 5.0,   'critical_low': 2.5,   'critical_high': 6.5},
            {'name': 'Chloride (Cl\u207b)',   'code': 'CL',  'unit': 'mmol/L', 'result_type': 'numeric', 'ref_min': 96.0,  'ref_max': 106.0},
            {'name': 'Bicarbonate (HCO\u2083\u207b)', 'code': 'HCO3', 'unit': 'mmol/L', 'result_type': 'numeric', 'ref_min': 22.0, 'ref_max': 29.0},
            {'name': 'Calcium (Ca\u00b2\u207a)',  'code': 'CA',  'unit': 'mg/dL', 'result_type': 'numeric', 'ref_min': 8.5, 'ref_max': 10.5,  'critical_low': 6.5,   'critical_high': 13.0},
        ],
    },

    # â”€â”€ SEROLOGY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        'name': 'HIV Rapid Test',
        'code': 'HIV-RAPID',
        'category': 'serology',
        'sample_type': 'Blood (Whole blood/Serum)',
        'price': 15000,
        'duration_hours': 1,
        'description': 'Rapid HIV-1/2 antibody screening.',
        'parameters': [
            {'name': 'HIV-1 Antibody', 'code': 'HIV1', 'unit': '', 'result_type': 'reactive_nonreactive', 'ref_text': 'Non-Reactive', 'flag_criteria': 'reactive_nonreactive'},
            {'name': 'HIV-2 Antibody', 'code': 'HIV2', 'unit': '', 'result_type': 'reactive_nonreactive', 'ref_text': 'Non-Reactive', 'flag_criteria': 'reactive_nonreactive'},
        ],
    },
    {
        'name': 'Hepatitis B Surface Antigen (HBsAg)',
        'code': 'HBSAG',
        'category': 'serology',
        'sample_type': 'Blood (Serum)',
        'price': 25000,
        'duration_hours': 24,
        'description': 'Hepatitis B infection screening.',
        'parameters': [
            {'name': 'HBsAg', 'code': 'HBSAG-V', 'unit': '', 'result_type': 'reactive_nonreactive', 'ref_text': 'Non-Reactive', 'flag_criteria': 'reactive_nonreactive'},
        ],
    },
    {
        'name': 'Hepatitis C Antibody (HCV)',
        'code': 'HCV',
        'category': 'serology',
        'sample_type': 'Blood (Serum)',
        'price': 30000,
        'duration_hours': 24,
        'description': 'Hepatitis C infection screening.',
        'parameters': [
            {'name': 'HCV Antibody', 'code': 'HCV-AB', 'unit': '', 'result_type': 'reactive_nonreactive', 'ref_text': 'Non-Reactive', 'flag_criteria': 'reactive_nonreactive'},
        ],
    },
    {
        'name': 'Syphilis (VDRL/RPR)',
        'code': 'VDRL',
        'category': 'serology',
        'sample_type': 'Blood (Serum)',
        'price': 20000,
        'duration_hours': 24,
        'description': 'Syphilis antibody screening.',
        'parameters': [
            {'name': 'VDRL/RPR', 'code': 'VDRL-V', 'unit': '', 'result_type': 'reactive_nonreactive', 'ref_text': 'Non-Reactive', 'flag_criteria': 'reactive_nonreactive'},
        ],
    },
    {
        'name': 'Malaria Rapid Test (mRDT)',
        'code': 'MALARIA-RDT',
        'category': 'serology',
        'sample_type': 'Blood (Whole blood)',
        'price': 10000,
        'duration_hours': 1,
        'description': 'Rapid malaria antigen detection.',
        'parameters': [
            {'name': 'P. falciparum Ag',     'code': 'PF-AG',  'unit': '', 'result_type': 'positive_negative', 'ref_text': 'Negative', 'flag_criteria': 'positive_negative'},
            {'name': 'P. vivax / other Ag',  'code': 'PV-AG',  'unit': '', 'result_type': 'positive_negative', 'ref_text': 'Negative', 'flag_criteria': 'positive_negative'},
        ],
    },
    {
        'name': 'Widal Test (Typhoid)',
        'code': 'WIDAL',
        'category': 'serology',
        'sample_type': 'Blood (Serum)',
        'price': 20000,
        'duration_hours': 24,
        'description': 'Typhoid fever antibody titre test.',
        'parameters': [
            {'name': 'S. Typhi O',      'code': 'W-TO',  'unit': 'titre', 'result_type': 'titer', 'ref_text': '<1:80', 'flag_criteria': 'range', 'ref_max': 80.0},
            {'name': 'S. Typhi H',      'code': 'W-TH',  'unit': 'titre', 'result_type': 'titer', 'ref_text': '<1:80', 'flag_criteria': 'range', 'ref_max': 80.0},
            {'name': 'S. Paratyphi AO', 'code': 'W-PAO', 'unit': 'titre', 'result_type': 'titer', 'ref_text': '<1:80', 'flag_criteria': 'range', 'ref_max': 80.0},
            {'name': 'S. Paratyphi BO', 'code': 'W-PBO', 'unit': 'titre', 'result_type': 'titer', 'ref_text': '<1:80', 'flag_criteria': 'range', 'ref_max': 80.0},
        ],
    },
    {
        'name': 'C-Reactive Protein (CRP)',
        'code': 'CRP',
        'category': 'serology',
        'sample_type': 'Blood (Serum)',
        'price': 20000,
        'duration_hours': 24,
        'description': 'Acute phase inflammation marker.',
        'parameters': [
            {'name': 'CRP', 'code': 'CRP-V', 'unit': 'mg/L', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 10.0, 'critical_high': 100.0},
        ],
    },
    {
        'name': 'Rheumatoid Factor (RF)',
        'code': 'RF',
        'category': 'serology',
        'sample_type': 'Blood (Serum)',
        'price': 25000,
        'duration_hours': 24,
        'description': 'Rheumatoid arthritis / autoimmune screening.',
        'parameters': [
            {'name': 'Rheumatoid Factor', 'code': 'RF-V', 'unit': 'IU/mL', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 20.0},
        ],
    },

    # â”€â”€ IMMUNOLOGY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        'name': 'Thyroid Function Test (TFT)',
        'code': 'TFT',
        'category': 'immunology',
        'sample_type': 'Blood (Serum)',
        'price': 55000,
        'duration_hours': 48,
        'description': 'Thyroid hormone panel.',
        'parameters': [
            {'name': 'TSH',      'code': 'TSH',  'unit': 'mIU/L',  'result_type': 'numeric', 'ref_min': 0.4,  'ref_max': 4.0,  'critical_low': 0.01, 'critical_high': 100.0},
            {'name': 'Free T3',  'code': 'FT3',  'unit': 'pg/mL',  'result_type': 'numeric', 'ref_min': 2.0,  'ref_max': 4.4},
            {'name': 'Free T4',  'code': 'FT4',  'unit': 'ng/dL',  'result_type': 'numeric', 'ref_min': 0.93, 'ref_max': 1.7},
        ],
    },
    {
        'name': 'Prostate Specific Antigen (PSA)',
        'code': 'PSA',
        'category': 'immunology',
        'sample_type': 'Blood (Serum)',
        'price': 45000,
        'duration_hours': 48,
        'description': 'Prostate cancer screening marker.',
        'parameters': [
            {'name': 'Total PSA', 'code': 'TPSA', 'unit': 'ng/mL', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 4.0, 'critical_high': 10.0},
            {'name': 'Free PSA',  'code': 'FPSA', 'unit': 'ng/mL', 'result_type': 'numeric', 'ref_min': 0.0, 'ref_max': 1.0},
        ],
    },
    {
        'name': 'Pregnancy Test (\u03b2-hCG)',
        'code': 'PREGNANCY',
        'category': 'immunology',
        'sample_type': 'Urine / Blood',
        'price': 10000,
        'duration_hours': 1,
        'description': 'Qualitative \u03b2-hCG pregnancy detection.',
        'parameters': [
            {'name': '\u03b2-hCG', 'code': 'BHCG', 'unit': '', 'result_type': 'positive_negative', 'ref_text': 'Negative (non-pregnant)', 'flag_criteria': 'positive_negative'},
        ],
    },

    # â”€â”€ PATHOLOGY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        'name': 'Urinalysis',
        'code': 'URINALYSIS',
        'category': 'pathology',
        'sample_type': 'Urine (Clean catch, mid-stream)',
        'price': 12000,
        'duration_hours': 2,
        'description': 'Complete urine examination â€” physical, chemical and microscopy.',
        'parameters': [
            {'name': 'Appearance',       'code': 'U-APP',  'unit': '',      'result_type': 'text',             'ref_text': 'Clear',            'flag_criteria': 'none'},
            {'name': 'Colour',           'code': 'U-COL',  'unit': '',      'result_type': 'text',             'ref_text': 'Pale Yellow',       'flag_criteria': 'none'},
            {'name': 'pH',               'code': 'U-PH',   'unit': '',      'result_type': 'numeric',          'ref_min': 4.5, 'ref_max': 8.0},
            {'name': 'Specific Gravity', 'code': 'U-SG',   'unit': '',      'result_type': 'numeric',          'ref_min': 1.005, 'ref_max': 1.030},
            {'name': 'Protein',          'code': 'U-PRO',  'unit': '',      'result_type': 'present_absent',   'ref_text': 'Absent',            'flag_criteria': 'present_absent'},
            {'name': 'Glucose',          'code': 'U-GLU',  'unit': '',      'result_type': 'present_absent',   'ref_text': 'Absent',            'flag_criteria': 'present_absent'},
            {'name': 'Ketones',          'code': 'U-KET',  'unit': '',      'result_type': 'present_absent',   'ref_text': 'Absent',            'flag_criteria': 'present_absent'},
            {'name': 'Blood',            'code': 'U-BLD',  'unit': '',      'result_type': 'present_absent',   'ref_text': 'Absent',            'flag_criteria': 'present_absent'},
            {'name': 'Nitrites',         'code': 'U-NIT',  'unit': '',      'result_type': 'positive_negative','ref_text': 'Negative',          'flag_criteria': 'positive_negative'},
            {'name': 'Leucocytes (WBC)', 'code': 'U-WBC',  'unit': '/HPF',  'result_type': 'numeric',          'ref_min': 0.0, 'ref_max': 5.0},
            {'name': 'Red Blood Cells',  'code': 'U-RBC',  'unit': '/HPF',  'result_type': 'numeric',          'ref_min': 0.0, 'ref_max': 2.0},
            {'name': 'Epithelial Cells', 'code': 'U-EPI',  'unit': '/HPF',  'result_type': 'text',             'ref_text': 'Few or Nil',        'flag_criteria': 'none'},
            {'name': 'Casts',            'code': 'U-CAST', 'unit': '',      'result_type': 'text',             'ref_text': 'None seen',         'flag_criteria': 'none'},
            {'name': 'Bacteria',         'code': 'U-BAC',  'unit': '',      'result_type': 'present_absent',   'ref_text': 'Absent',            'flag_criteria': 'present_absent'},
        ],
    },
    {
        'name': 'Stool Analysis',
        'code': 'STOOL-EXAM',
        'category': 'pathology',
        'sample_type': 'Stool (Fresh sample)',
        'price': 15000,
        'duration_hours': 4,
        'description': 'Stool for ova, parasites, occult blood and microscopy.',
        'parameters': [
            {'name': 'Consistency',   'code': 'ST-CON',  'unit': '', 'result_type': 'text',             'ref_text': 'Formed',         'flag_criteria': 'none'},
            {'name': 'Colour',        'code': 'ST-COL',  'unit': '', 'result_type': 'text',             'ref_text': 'Brown',          'flag_criteria': 'none'},
            {'name': 'Mucus',         'code': 'ST-MUC',  'unit': '', 'result_type': 'present_absent',   'ref_text': 'Absent',         'flag_criteria': 'present_absent'},
            {'name': 'Occult Blood',  'code': 'ST-OBL',  'unit': '', 'result_type': 'positive_negative','ref_text': 'Negative',       'flag_criteria': 'positive_negative'},
            {'name': 'Ova/Parasites', 'code': 'ST-OVA',  'unit': '', 'result_type': 'present_absent',   'ref_text': 'Not seen',       'flag_criteria': 'present_absent'},
            {'name': 'Cysts',         'code': 'ST-CYS',  'unit': '', 'result_type': 'present_absent',   'ref_text': 'Not seen',       'flag_criteria': 'present_absent'},
            {'name': 'WBCs (Pus cells)', 'code': 'ST-WBC', 'unit': '/HPF', 'result_type': 'numeric',   'ref_min': 0.0, 'ref_max': 5.0},
            {'name': 'RBCs',          'code': 'ST-RBC',  'unit': '/HPF', 'result_type': 'numeric',      'ref_min': 0.0, 'ref_max': 2.0},
        ],
    },
    {
        'name': 'Semen Analysis',
        'code': 'SEMEN',
        'category': 'pathology',
        'sample_type': 'Semen (Fresh, within 60 min)',
        'price': 35000,
        'duration_hours': 4,
        'description': 'Sperm count, motility, morphology and volume analysis.',
        'parameters': [
            {'name': 'Volume',              'code': 'SEM-VOL',  'unit': 'mL',  'result_type': 'numeric',    'ref_min': 1.5,  'ref_max': 6.8},
            {'name': 'pH',                  'code': 'SEM-PH',   'unit': '',    'result_type': 'numeric',    'ref_min': 7.2,  'ref_max': 8.0},
            {'name': 'Liquefaction Time',   'code': 'SEM-LIQ',  'unit': 'min', 'result_type': 'numeric',    'ref_min': 0.0,  'ref_max': 60.0},
            {'name': 'Sperm Concentration', 'code': 'SEM-CONC', 'unit': 'M/mL', 'result_type': 'numeric',  'ref_min': 15.0, 'ref_max': 999.0},
            {'name': 'Total Motility',      'code': 'SEM-MOT',  'unit': '%',   'result_type': 'percentage', 'ref_min': 40.0, 'ref_max': 100.0},
            {'name': 'Progressive Motility','code': 'SEM-PROG', 'unit': '%',   'result_type': 'percentage', 'ref_min': 32.0, 'ref_max': 100.0},
            {'name': 'Normal Forms',        'code': 'SEM-NORM', 'unit': '%',   'result_type': 'percentage', 'ref_min': 4.0,  'ref_max': 100.0},
        ],
    },

    # â”€â”€ MICROBIOLOGY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    {
        'name': 'Urine Culture & Sensitivity',
        'code': 'URINE-CS',
        'category': 'microbiology',
        'sample_type': 'Urine (Sterile container)',
        'price': 45000,
        'duration_hours': 72,
        'description': 'UTI organism identification and antibiotic sensitivity.',
        'parameters': [
            {'name': 'Colony Count',     'code': 'UC-COUNT',  'unit': 'CFU/mL', 'result_type': 'text',             'ref_text': '<10,000 or No growth',  'flag_criteria': 'none'},
            {'name': 'Organism Grown',   'code': 'UC-ORG',    'unit': '',       'result_type': 'text',             'ref_text': 'No growth',             'flag_criteria': 'none'},
            {'name': 'Sensitivity',      'code': 'UC-SENS',   'unit': '',       'result_type': 'text',             'ref_text': 'N/A',                   'flag_criteria': 'none'},
        ],
    },
    {
        'name': 'Blood Culture & Sensitivity',
        'code': 'BLOOD-CS',
        'category': 'microbiology',
        'sample_type': 'Blood (Culture bottle)',
        'price': 60000,
        'duration_hours': 120,
        'description': 'Septicaemia organism identification and sensitivity.',
        'parameters': [
            {'name': 'Growth',         'code': 'BC-GROW',  'unit': '', 'result_type': 'present_absent', 'ref_text': 'No growth', 'flag_criteria': 'present_absent'},
            {'name': 'Organism',       'code': 'BC-ORG',   'unit': '', 'result_type': 'text',           'ref_text': 'N/A',       'flag_criteria': 'none'},
            {'name': 'Sensitivity',    'code': 'BC-SENS',  'unit': '', 'result_type': 'text',           'ref_text': 'N/A',       'flag_criteria': 'none'},
        ],
    },
    {
        'name': 'Sputum Culture & Sensitivity',
        'code': 'SPUTUM-CS',
        'category': 'microbiology',
        'sample_type': 'Sputum (Sterile container, morning)',
        'price': 40000,
        'duration_hours': 72,
        'description': 'Respiratory infection organism identification.',
        'parameters': [
            {'name': 'Growth',       'code': 'SC-GROW', 'unit': '', 'result_type': 'present_absent', 'ref_text': 'Normal respiratory flora', 'flag_criteria': 'present_absent'},
            {'name': 'Organism',     'code': 'SC-ORG',  'unit': '', 'result_type': 'text',           'ref_text': 'N/A',                     'flag_criteria': 'none'},
            {'name': 'Sensitivity',  'code': 'SC-SENS', 'unit': '', 'result_type': 'text',           'ref_text': 'N/A',                     'flag_criteria': 'none'},
        ],
    },
    {
        'name': 'AFB Sputum (TB Smear)',
        'code': 'AFB',
        'category': 'microbiology',
        'sample_type': 'Sputum (3 samples, morning)',
        'price': 20000,
        'duration_hours': 24,
        'description': 'Acid-fast bacilli smear for tuberculosis screening.',
        'parameters': [
            {'name': 'AFB Smear Result', 'code': 'AFB-V', 'unit': '', 'result_type': 'positive_negative', 'ref_text': 'Negative', 'flag_criteria': 'positive_negative'},
            {'name': 'Grading',          'code': 'AFB-G', 'unit': '', 'result_type': 'text',              'ref_text': 'Negative', 'flag_criteria': 'none'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Clears existing lab data and populates tests with full profiles and parameters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete ALL existing LabTest, TestProfile, TestParameter data first',
        )

    def handle(self, *args, **options):
        if options['clear']:
            # Remove results first (FK cascade order)
            pr_count = ParameterResult.objects.count()
            ParameterResult.objects.all().delete()
            res_count = LabTestResult.objects.count()
            LabTestResult.objects.all().delete()
            req_count = LabTestRequest.objects.count()
            LabTestRequest.objects.all().delete()
            t_count = LabTest.objects.count()
            LabTest.objects.all().delete()
            pp_count = TestProfileParameter.objects.count()
            TestProfileParameter.objects.all().delete()
            p_count = TestProfile.objects.count()
            TestProfile.objects.all().delete()
            param_count = TestParameter.objects.count()
            TestParameter.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f'Deleted: {t_count} tests, {p_count} profiles, {param_count} parameters, '
                f'{pp_count} profile-params, {res_count} results, {pr_count} param-results, '
                f'{req_count} requests'
            ))

        self._create_tests()

    def _create_tests(self):
        created = 0
        for td in TESTS:
            if LabTest.objects.filter(code=td['code']).exists():
                self.stdout.write(self.style.WARNING(f'Skipped (exists): {td["name"]}'))
                continue
            self._make_test(td)
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created: {td["name"]} ({td["code"]})'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'Done. {created} test(s) created out of {len(TESTS)} defined.'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

    def _make_test(self, td):
        params = []
        for i, pd in enumerate(td.get('parameters', [])):
            param, _ = TestParameter.objects.get_or_create(
                code=pd['code'],
                defaults={
                    'name':                 pd['name'],
                    'result_type':          pd.get('result_type', 'numeric'),
                    'unit':                 pd.get('unit', ''),
                    'reference_range_min':  pd.get('ref_min'),
                    'reference_range_max':  pd.get('ref_max'),
                    'reference_range_text': pd.get('ref_text', ''),
                    'flag_criteria':        pd.get('flag_criteria', 'range'),
                    'critical_low':         pd.get('critical_low'),
                    'critical_high':        pd.get('critical_high'),
                    'display_order':        i + 1,
                    'is_active':            True,
                }
            )
            params.append((i + 1, param))

        profile = TestProfile.objects.create(
            name=td['name'] + ' Profile',
            code=td['code'] + '-PROF',
            category=td['category'],
            sample_type=td.get('sample_type', ''),
            duration_hours=td.get('duration_hours', 4),
            price=td.get('price', 0),
            currency='UGX',
            description=td.get('description', ''),
            is_active=True,
        )

        for order, param in params:
            TestProfileParameter.objects.create(
                profile=profile,
                parameter=param,
                display_order=order,
            )

        LabTest.objects.create(
            name=td['name'],
            code=td['code'],
            category=td['category'],
            sample_type=td.get('sample_type', ''),
            price=td.get('price', 0),
            currency='UGX',
            duration_hours=td.get('duration_hours', 4),
            description=td.get('description', ''),
            profile=profile,
            is_active=True,
        )
