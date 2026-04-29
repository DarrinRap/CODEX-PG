using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

namespace AMMockupReviewLauncher
{
    internal static class Program
    {
        private const string TargetPath = @"C:\CODEX PG\CODEX AM Screen B v2 CC Review Render 1440x1200.png";

        [STAThread]
        private static void Main()
        {
            try
            {
                if (!File.Exists(TargetPath))
                {
                    MessageBox.Show("The AM Mockup Review render could not be found:\n\n" + TargetPath, "AM Mockup Review", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                Process.Start(new ProcessStartInfo
                {
                    FileName = TargetPath,
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "AM Mockup Review", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}