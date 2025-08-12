import pandas as pd

# Function to analyze top fields in a DataFrame
def analyze_top_fields(nil_importers, group_by_cols, agg_dict, sort_by, top_n, csv_filename, empty_fields, display_mode):
    # Ensure empty_fields is initialized
    if empty_fields is None:
        empty_fields = []
    # This ensures that fields that are aggregated as 'first' are treated as empty in the output
    if isinstance(empty_fields, str):
        # If empty_fields is a string, convert it to a list
        empty_fields = [empty_fields]
    # If empty_fields is a list, ensure it contains unique values
    elif isinstance(empty_fields, list):
        empty_fields += [key for key, value in agg_dict.items() if value == 'first' and key not in empty_fields]
        empty_fields = list(set(empty_fields))
    else:
        raise ValueError("empty_fields must be a string or a list of strings")

    # Determine if we need to add totals or not based on display_mode
    if display_mode == 'all':
        # Display the entire dataset and add a single row with overall totals at the end
        add_totals = True
        add_remaining = False
        top_n = len(nil_importers)  # Display all records
    elif display_mode == 'None':
        # Display all records without additional totals
        add_totals = False
        add_remaining = False
        top_n = len(nil_importers)  # Display all records
    else:
        # Normal processing
        add_totals = True
        add_remaining = True

    # Step 1: Grouping and sorting to get top N records
    top_field_amounts = (
        nil_importers.groupby(group_by_cols).agg(agg_dict).sort_values(by=sort_by, ascending=False).head(top_n).reset_index()
        )

    if add_totals:
        # Step 2: Aggregating remaining records (only those not in the top N)
        remaining_values = {}
        for key in agg_dict.keys():
            if key in empty_fields:
                remaining_values[key] = ''  # Empty for specified fields
            else:
                remaining_values[key] = nil_importers[~nil_importers[group_by_cols[0]].isin(top_field_amounts[group_by_cols[0]])][key].agg(agg_dict[key])

        # Step 3: Counting the remaining records
        remaining_field_count = nil_importers[~nil_importers[group_by_cols[0]].isin(top_field_amounts[group_by_cols[0]])][group_by_cols[0]].nunique()

        # Step 4: Calculating totals from the entire DataFrame
        totals_row = pd.DataFrame([{
            group_by_cols[0]: 'Grand Totals',
            **{key: nil_importers[key].sum() if agg_dict[key] == 'sum' else nil_importers[key].nunique() if agg_dict[key] == 'nunique' or agg_dict[key] == 'count' else '' for key in agg_dict.keys()},
            **{key: '' for key in empty_fields}  # Empty fields for the 'Totals' row
        }])

        if display_mode == 'all':
            # Return the entire dataset with a single row of overall totals at the end
            analysis_result = pd.concat([top_field_amounts, totals_row], ignore_index=True)
        else:
            # Step 5: Creating the 'Remaining' row dynamically
            remaining_row = pd.DataFrame([{
                group_by_cols[0]: f'Other {remaining_field_count} {group_by_cols[0].capitalize()}',
                **remaining_values  # Use aggregated or empty fields dynamically
            }])
            
            # Step 6: Calculating top N totals
            top_totals = pd.DataFrame([{
                group_by_cols[0]: f'Top {top_n} Totals',
                **{key: top_field_amounts[key].sum() if agg_dict[key] == 'sum' else top_field_amounts[key].sum() if agg_dict[key] == 'nunique' else '' for key in agg_dict.keys()},
                **{key: '' for key in empty_fields}  # Leave empty fields blank
            }])

            # Step 7: Appending the Remaining & Total rows to the DataFrame
            analysis_result = pd.concat([top_field_amounts, top_totals, remaining_row, totals_row], ignore_index=True)
    else:
        # Display all records without additional totals
        analysis_result = top_field_amounts

    # Step 8: Save the result to CSV
    analysis_result.to_csv(f'results/{csv_filename}', index=None)

    return analysis_result.to_html(classes="table table-striped", index = False, border=0)
    # return analysis_result
