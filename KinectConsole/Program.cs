using System;
using System.Threading;
using Microsoft.Kinect;
using System.Collections.Generic;
using System.Text;
using System.Globalization;

namespace KinectConsole
{
    class KinectProgram
    {
        KinectSensor _sensor;
        MultiSourceFrameReader _reader;
        IList<Body> _bodies;

        IList<JointType> joints;
        IList<float> joint_positions;
        
        bool detected_body;

        const float AVG_PERCENT = 0.2f;
        float applied_avg = 1.0f; //For first frame (avoid conditionals)

        public void Initialize()
        {
            _sensor = KinectSensor.GetDefault();

            if (_sensor != null)
            {
                _sensor.Open();

                _reader = _sensor.OpenMultiSourceFrameReader(FrameSourceTypes.Color | FrameSourceTypes.Depth | FrameSourceTypes.Infrared | FrameSourceTypes.Body);
                _reader.MultiSourceFrameArrived += Reader_MultiSourceFrameArrived;
            }

            detected_body = false;

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
                JointType.FootRight,

                JointType.SpineShoulder

                //Exclude hands
            };

            joint_positions = new List<float>(new float[joints.Count*3]);
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
            if (!detected_body) return "";

            //Reset state
            detected_body = false;

            StringBuilder finalString = new StringBuilder();

            for (int i=0; i<joint_positions.Count; i++)
            {
                finalString.AppendFormat(CultureInfo.InvariantCulture, "{0:0.000},", joint_positions[i]);
            }

            // Remove the trailing comma
            if (finalString.Length > 0)
                finalString.Length--;
            
            return finalString.ToString();
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

                        for (int i=0; i<joints.Count; i++)
                        {
                            var position = body.Joints[joints[i]].Position;

                            joint_positions[i * 3 + 0] = position.X * applied_avg + joint_positions[i * 3 + 0] * (1.0f - applied_avg);
                            joint_positions[i * 3 + 1] = position.Y * applied_avg + joint_positions[i * 3 + 1] * (1.0f - applied_avg);
                            joint_positions[i * 3 + 2] = position.Z * applied_avg + joint_positions[i * 3 + 2] * (1.0f - applied_avg);

                        }

                        applied_avg = AVG_PERCENT; //Set after first frame
                        detected_body = true;
                        break;
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
