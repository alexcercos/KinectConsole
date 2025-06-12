using System;
using System.Threading;
using Microsoft.Kinect;
using System.Collections.Generic;
using System.Text;

namespace KinectConsole
{
    class KinectProgram
    {
        KinectSensor _sensor;
        MultiSourceFrameReader _reader;
        IList<Body> _bodies;

        IList<JointType> joints;

        public string current_info;

        public void Initialize()
        {
            _sensor = KinectSensor.GetDefault();

            if (_sensor != null)
            {
                _sensor.Open();

                _reader = _sensor.OpenMultiSourceFrameReader(FrameSourceTypes.Color | FrameSourceTypes.Depth | FrameSourceTypes.Infrared | FrameSourceTypes.Body);
                _reader.MultiSourceFrameArrived += Reader_MultiSourceFrameArrived;
            }

            joints = new List<JointType> {
                JointType.SpineBase,
                JointType.SpineMid,
                JointType.Neck,
                JointType.Head,

                JointType.ShoulderLeft,
                JointType.ElbowLeft,
                JointType.WristLeft,
                JointType.HandLeft,

                JointType.ShoulderRight,
                JointType.ElbowRight,
                JointType.WristRight,
                JointType.HandRight,

                JointType.HipLeft,
                JointType.KneeLeft,
                JointType.AnkleLeft,
                JointType.FootLeft,

                JointType.HipRight,
                JointType.KneeRight,
                JointType.AnkleRight,
                JointType.FootRight

                //Exclude hands
            };
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

        public string GetCurrentInfo()
        {
            return current_info;
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

                        StringBuilder jointPositions = new StringBuilder();

                        foreach (JointType joint in joints)
                        {
                            var position = body.Joints[joint].Position;
                            jointPositions.AppendFormat("{0:0.000},{1:0.000},{2:0.000},", position.X, position.Y, position.Z);
                        }

                        // Remove the trailing comma
                        if (jointPositions.Length > 0)
                            jointPositions.Length--;

                        current_info = jointPositions.ToString();
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
                Thread.Sleep(100);
                Console.WriteLine(kinect_program.GetCurrentInfo());
            }
            
        }
    }
}
