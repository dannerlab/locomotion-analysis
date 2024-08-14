import pandas as pd
import os

class StepTable:

    def __init__(self):
        self.step_table = pd.DataFrame()

    def __init__(self, step_table):
        self.step_table = step_table
        self.columns = step_table.columns

    def import_kinematics(self, h5_path):
        #imports the kinematics portion of the hdf
        if not os.path.exists(h5_path):
            print(f"File not found: {h5_path}")
            return None
        key = 'df_kinematics'
        kinematics_df = pd.read_hdf(h5_path, key)
        return kinematics_df

    def add_position_stats(self):

        toe_tip_x_max = []
        toe_tip_x_min = []
        toe_tip_x_end = []
        toe_tip_x_excursion = []
        toe_tip_y_max = []
        iliac_crest_y_max = []
        iliac_crest_y_min = []
        iliac_crest_y_excursion = []

        for step_i, trial in self.step_table.iterrows():
            h5_path = trial['source-data-h5-path']
            h5_df = self.import_kinematics(h5_path)

            # Get step slice
            start = trial['swing-start-idx']
            stop = trial['stance-stop-idx']
            step_slice = h5_df[start:stop]

            # Calculate x toe statistics normalized to hip x
            slice_toe_x = step_slice['ToeTip_x'] - step_slice['Hip_x']
            toe_tip_x_max.append(slice_toe_x.max())
            toe_tip_x_min.append(slice_toe_x.min())
            toe_tip_x_end.append(slice_toe_x.iloc[-1])

            # Calculate y toe & crest statistics
            toe_tip_y_max.append(step_slice['ToeTip_y'].max())
            iliac_crest_y_max.append(step_slice['IliacCrest_y'].max())
            iliac_crest_y_min.append(step_slice['IliacCrest_y'].min())

        # Assign the calculated statistics back to the DataFrame
        self.step_table['ToeTip-x-max'] = toe_tip_x_max
        self.step_table['ToeTip-x-min'] = toe_tip_x_min
        self.step_table['ToeTip-x-end'] = toe_tip_x_end

        self.step_table['ToeTip-y-max'] = toe_tip_y_max
        self.step_table['IliacCrest-y-max'] = iliac_crest_y_max
        self.step_table['IliacCrest-y-max'] = iliac_crest_y_min

    def calc_discrete_stats(self):
        self.step_table['ToeTip-x-excursion'] = self.step_table['ToeTip-x-max'] - self.step_table['ToeTip-x-min']
        self.step_table['IliacCrest-y-excursion'] = self.step_table['IliacCrest-y-max'] - self.step_table['IliacCrest-y-max']
        self.step_table['step-duration'] = self.step_table['stance-stop'] - self.step_table['swing-start']
        self.step_table['cycle-velocity'] = (self.step_table['ToeTip-x-end'] - self.step_table['ToeTip-x-max']) + self.step_table['belt-speed'] * self.step_table['swing-duration'] / self.step_table['step-duration']
        self.step_table['duty-factor'] = (self.step_table['stance-duration']) / (self.step_table['step-duration'])
        self.step_table['stride-length'] = (self.step_table['ToeTip-x-end'] - self.step_table['ToeTip-x-min']) + self.step_table['belt-speed'] * self.step_table['swing-duration']

    def add_second_swing(self):
        #adds columns to facilitate easy selection of steps that consist of a stance phase followed by a swing phase
        #recommend using this rather than indexing through each time because it handles mouse & trial separation

        swing_cols = ['swing-start', 'swing-stop', 'swing-duration', 'swing-start-idx', 'swing-stop-idx']

        second_step_table = pd.DataFrame()
        for mouse_id in self.step_table['mouse-id'].unique():
            for trial in self.step_table['trial-number'].unique():
                mouse_id_trial_df = self.step_table[(self.step_table['mouse-id'] == mouse_id) & (self.step_table['trial-number'] == trial)] #selects all steps from one trial
                mouse_id_trial_df_second = mouse_id_trial_df.copy()
                for col in swing_cols:
                    mouse_id_trial_df_second[f'second-{col}'] = mouse_id_trial_df[col].shift(-1) #.shift(-1) shifts the column values up by one and fills with NaN
                second_step_table = pd.concat([second_step_table, mouse_id_trial_df_second], ignore_index=True)
        self.step_table = second_step_table

def test():
    step_table_not_class = pd.read_csv('Sample_data/step_table.csv')
    step_table = StepTable(step_table_not_class)
    step_table.add_position_stats()
    step_table.calc_discrete_stats()
    step_table.add_second_swing()
    print(step_table.columns)

if __name__ == "__main__":
    test()