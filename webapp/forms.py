from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Email

class ActionsForm(FlaskForm):
    action = SelectField(u'Tools', 
                         id="action_command",
                         choices=[
                            ('update_status', 'Check Status & Update'), 
                            ('wake_lan', 'Wake on Lan'),
                            ('wake_amt', 'Wake on AMT'),
                            ('get_trendmicro_version', 'Get Trendmicro Info'),
                            ('get_trendmicro_version_api', 'Get Trendmicro Version API'),
                            ('cmd_update_w10', 'Update to Windows 10 Latest version'),
                            ('cmd_uninstall_tm', 'Run the Trendmicro Uninstaller'),
                            ('cmd_install_tm', 'Run the Trendmicro Installer'),
                            ('get_win10_version', 'Get Win10 Version'),
                            ('get_hw_vendor', 'Get HW Vendor & Model'),
                            ('cmd_reboot', 'Reboot a remote Host'),
                            ('get_wmi_query_last_logged', 'Get last Logged user'),
                            ('get_sccm_info', 'Get SCCM Version'),
                            ('cmd_run_all_collectors', 'Run all collectors')
                            
                           ])
    hosts = HiddenField(u'Hosts',id="action_hosts")
    submit = SubmitField(u'Run', id="action_submit")
    histnav = HiddenField(u'Hosts',id="histnav")

class ActionsFormCheck(FlaskForm):
    action  = HiddenField(u'Hosts',id="action")
    hosts   = HiddenField(u'Hosts',id="hosts")
    histnav = HiddenField(u'Hosts',id="histnav")
    #submit is done via js on template