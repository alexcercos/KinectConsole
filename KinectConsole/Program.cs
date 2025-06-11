using System;
using System.Threading;
using Microsoft.Kinect;
using System.Collections.Generic;

namespace KinectConsole
{
    class KinectProgram
    {
        KinectSensor _sensor;
        MultiSourceFrameReader _reader;
        IList<Body> _bodies;

        public void Initialize()
        {
            _sensor = KinectSensor.GetDefault();

            if (_sensor != null)
            {
                _sensor.Open();

                _reader = _sensor.OpenMultiSourceFrameReader(FrameSourceTypes.Color | FrameSourceTypes.Depth | FrameSourceTypes.Infrared | FrameSourceTypes.Body);
                _reader.MultiSourceFrameArrived += Reader_MultiSourceFrameArrived;
            }
        }

        public void Deinitialize()
        {
            if (_reader != null)
            {
                _reader.Dispose();
            }

            if (_sensor != null)
            {
                _sensor.Close();
            }
        }

        void Reader_MultiSourceFrameArrived(object sender, MultiSourceFrameArrivedEventArgs e)
        {
            var reference = e.FrameReference.AcquireFrame();

            // Body
            using (var frame = reference.BodyFrameReference.AcquireFrame())
            {
                if (frame != null)
                {
                    _bodies = new Body[frame.BodyFrameSource.BodyCount];

                    frame.GetAndRefreshBodyData(_bodies);

                    foreach (var body in _bodies)
                    {
                        if (body == null)
                            continue;
                        
                        if (!body.IsTracked)
                            continue;

                        Console.WriteLine("BODY DETECTED");
                        // Draw skeleton.
                        //if (_displayBody)
                        //{
                        //    canvas.DrawSkeleton(body);
                        //    _recorder.Update(body);
                        //}
                    }
                }
            }
        }
    }


    class Program
    {
        static volatile bool keepRunning = true;
        static volatile KinectProgram kinect_program;

        static void Main(string[] args)
        {
            Console.WriteLine("Starting loop. Press Ctrl+C or send termination to stop.");

            // STARTUP

            kinect_program = new KinectProgram();
            kinect_program.Initialize();

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

                kinect_program.Deinitialize();
            };

            while (keepRunning)
            {
                Console.WriteLine("Test output");

                Thread.Sleep(500);
            }
            
        }
    }
}
