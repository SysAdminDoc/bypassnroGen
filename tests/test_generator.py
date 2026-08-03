import unittest
import xml.etree.ElementTree as ET
import tkinter as tk

from BypassNRO_Generator import APP_VERSION, BypassNROGenerator


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = BypassNROGenerator(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_generates_arm64_audit_disk_and_extra_accounts(self):
        self.app.target_architecture.set("arm64")
        self.app.audit_mode.set(True)
        self.app.enable_disk_partitioning.set(True)
        self.app.additional_accounts_text.delete("1.0", "end")
        self.app.additional_accounts_text.insert("1.0", "Tech,Technician,Administrators,S3cret\nUser,,Users,")

        xml = self.app.generate_unattend_xml()
        ET.fromstring(xml)

        self.assertIn(f"Version: {APP_VERSION}", xml)
        self.assertIn('processorArchitecture="arm64"', xml)
        self.assertIn("<DiskConfiguration>", xml)
        self.assertIn("<Mode>Audit</Mode>", xml)
        self.assertIn("<Name>Tech</Name>", xml)
        self.assertIn("<Name>User</Name>", xml)

    def test_bypass_cmd_can_launch_localonly_uri(self):
        self.app.msa_localonly_bypass.set(True)

        cmd = self.app.generate_bypass_cmd()

        self.assertIn("ms-cxh://setaddlocalonly", cmd)

    def test_bloatware_mode_can_remove_provisioned_only(self):
        self.app.set_all_bloatware(False)
        self.app.bloatware_apps["Microsoft.BingNews"].set(True)
        self.app.bloatware_app_modes["Microsoft.BingNews"].set("Provisioned only")

        xml = self.app.generate_unattend_xml()

        self.assertIn("Remove-AppxProvisionedPackage", xml)
        self.assertNotIn("Remove-AppxPackage -AllUsers", xml)

    def test_optional_export_generators_render_expected_helpers(self):
        self.assertIn("oscdimg.exe", self.app.generate_iso_helper_ps1())
        self.assertIn("DriveLetter", self.app.generate_usb_helper_ps1())
        self.assertIn("wpeinit", self.app.generate_startnet_cmd())
        self.assertIn("Registry Reference", self.app.generate_registry_reference_html())
        self.assertIn("validation report", self.app.generate_validation_report())

    def test_profile_roundtrip_includes_new_fields(self):
        self.app.target_architecture.set("arm64")
        self.app.output_iso_helper.set(True)
        self.app.completion_webhook_url.set("https://example.test/hook")
        self.app.bloatware_app_modes["Microsoft.BingNews"].set("Provisioned only")

        profile = self.app._get_profile_dict()
        self.app.target_architecture.set("amd64")
        self.app.output_iso_helper.set(False)
        self.app.completion_webhook_url.set("")
        self.app.bloatware_app_modes["Microsoft.BingNews"].set("Provisioned + per-user")
        self.app._load_profile_dict(profile)

        self.assertEqual(self.app.target_architecture.get(), "arm64")
        self.assertTrue(self.app.output_iso_helper.get())
        self.assertEqual(self.app.completion_webhook_url.get(), "https://example.test/hook")
        self.assertEqual(self.app.bloatware_app_modes["Microsoft.BingNews"].get(), "Provisioned only")


if __name__ == "__main__":
    unittest.main()
