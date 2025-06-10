using System;
using System.Threading;

namespace KinectConsole
{
    class Program
    {
        static volatile bool keepRunning = true;

        static void Main(string[] args)
        {
            Console.WriteLine("Starting loop. Press Ctrl+C or send termination to stop.");

            // Hook Ctrl+C
            Console.CancelKeyPress += (sender, e) =>
            {
                Console.WriteLine("Ctrl+C detected!");
                e.Cancel = true; // Prevent immediate termination
                keepRunning = false;
            };

            // Hook process exit (works for .Terminate(), closing console, etc.)
            AppDomain.CurrentDomain.ProcessExit += (sender, e) =>
            {
                Console.WriteLine("Process is exiting.");
                // No need to set keepRunning here because process will exit
            };

            while (keepRunning)
            {
                Console.WriteLine("Test output");

                Thread.Sleep(500);
            }
            
        }
    }
}
