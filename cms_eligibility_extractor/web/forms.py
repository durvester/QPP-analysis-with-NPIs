"""
WTForms for secure file uploads and processing configuration.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectMultipleField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget
import csv
import io

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes."""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class NPIUploadForm(FlaskForm):
    """Form for uploading NPI CSV files and configuring processing."""
    
    # File upload
    npi_file = FileField(
        'NPI CSV File',
        validators=[
            FileRequired(message='Please select a CSV file'),
            FileAllowed(['csv'], message='Only CSV files are allowed')
        ]
    )
    
    # Year selection
    years = MultiCheckboxField(
        'Processing Years',
        choices=[
            ('2023', '2023'),
            ('2024', '2024'), 
            ('2025', '2025')
        ],
        validators=[DataRequired(message='Please select at least one year')],
        default=['2024', '2025']
    )
    
    # Processing options
    save_raw_responses = BooleanField(
        'Save Raw API Responses',
        default=True,
        description='Save raw JSON responses for debugging'
    )
    
    parallel_processing = BooleanField(
        'Parallel Processing',
        default=True,
        description='Process years in parallel for faster execution'
    )
    
    batch_size = IntegerField(
        'Batch Size',
        validators=[NumberRange(min=1, max=1000)],
        default=100,
        description='Number of NPIs to process in each batch'
    )
    
    submit = SubmitField('Start Processing')
    
    def validate_npi_file(self, field):
        """Custom validator for NPI CSV file format."""
        if field.data:
            try:
                # Read file content
                file_content = field.data.read()
                field.data.seek(0)  # Reset file pointer
                
                # Try to parse as CSV
                csv_content = file_content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                # Check for required columns
                fieldnames = csv_reader.fieldnames
                if not fieldnames:
                    raise ValueError("CSV file appears to be empty")
                
                # Look for NPI column (case insensitive)
                npi_column = None
                for col in fieldnames:
                    if col.lower() in ['npi', 'npis', 'npi_number']:
                        npi_column = col
                        break
                
                if not npi_column:
                    raise ValueError("CSV file must contain an 'npi' column")
                
                # Validate first few rows have NPI-like values
                rows_checked = 0
                for row in csv_reader:
                    if rows_checked >= 5:  # Check first 5 rows
                        break
                    
                    npi_value = row.get(npi_column, '').strip()
                    if npi_value and not (npi_value.isdigit() and len(npi_value) == 10):
                        raise ValueError(f"Invalid NPI format in row {rows_checked + 1}: {npi_value}")
                    
                    rows_checked += 1
                
                if rows_checked == 0:
                    raise ValueError("CSV file contains no data rows")
                    
            except UnicodeDecodeError:
                raise ValueError("File must be a valid UTF-8 encoded CSV")
            except csv.Error as e:
                raise ValueError(f"Invalid CSV format: {str(e)}")
            except Exception as e:
                raise ValueError(f"File validation error: {str(e)}")


class JobStatusForm(FlaskForm):
    """Form for checking job status."""
    refresh = SubmitField('Refresh Status')