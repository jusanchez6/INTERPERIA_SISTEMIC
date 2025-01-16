#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <iostream>
#include <string>
#include <chrono>
#include <thread>

using namespace cv;
using namespace std;

#define MODE_MULTITOMA 1
#define MODE_TOMAUNICA 0

/// Redefinir para cambiar el modo de toma
#define MODE MODE_TOMAUNICA

// Toma muchas fotos y solo guarda la ultima
// Comenta esta parte para usar el modo de captura unica

// --------------------------------------------------------------------------------------------------------------------------------------------------------------------

#if (MODE==MODE_MULTITOMA)
    const int FRAME_RATE = 23; // Tasa de fotogramas deseada

    int main(int argc, char** argv)
    {
        if (argc != 2) {
            cerr << "Uso: " << argv[0] << " <dispositivo>" << endl;
            cerr << "Ejemplo: " << argv[0] << " /dev/video0" << endl;
            return -1;
        }

        string str = argv[1];

        string gstformat = "NV12";
        string gstfile = "v4l2src device=" + str + " ! video/x-raw,format=" + gstformat + ",width=1920,height=1080,framerate=30/1 ! videoconvert ! appsink";
        VideoCapture capture(gstfile);

        if (!capture.isOpened()) {
            cerr << "Error al abrir la camara." << endl;
            return -1;
        }

        cout << "Iniciando captura a " << FRAME_RATE << " FPS. Presione Ctrl+C para detener." << endl;

        int frame_count = 0;
        auto frame_duration = std::chrono::milliseconds(1000 / FRAME_RATE);

        while (true) {
            auto start_time = std::chrono::high_resolution_clock::now();
            
            Mat frame;
            capture >> frame;

            if (frame.empty()) {
                cerr << "No se pudo capturar el frame." << endl;
                continue;
            }

            string filename = "current_frame.jpg";
            bool success = imwrite(filename, frame);

            if (success) {
                cout << "Frame guardado como " << filename << endl;
                frame_count++;
            } else {
                cerr << "Error al guardar el frame." << endl;
                break;
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
            
            // Esperar el tiempo restante para alcanzar la tasa de fotogramas deseada
            if (elapsed_time < frame_duration) {
                std::this_thread::sleep_for(frame_duration - elapsed_time);
            }
        }

        capture.release();
        return 0;
    }

// --------------------------------------------------------------------------------------------------------------------------------------------------------------------


// Toma solo un frame y lo guarda en un archivo
// Comenta esta parte para usar el modo de captura continua
// --------------------------------------------------------------------------------------------------------------------------------------------------------------------

#elif (MODE==MODE_TOMAUNICA)
    int main(int argc, char** argv)
    {
        if (argc != 2) {
            cerr << "Uso: " << argv[0] << " <dispositivo>" << endl;
            cerr << "Ejemplo: " << argv[0] << " /dev/video0" << endl;
            return -1;
        }

        string str = argv[1];

        // Configuración de GStreamer
        string gstformat = "NV12";
        string gstfile = "v4l2src device=" + str + " ! video/x-raw,format=" + gstformat + ",width=1920,height=1080,framerate=30/1 ! videoconvert ! appsink";
        VideoCapture capture(gstfile);

        if (!capture.isOpened()) {
            cerr << "Error al abrir la cámara." << endl;
            return -1;
        }

        cout << "Capturando un frame. Presione Ctrl+C para detener." << endl;

        Mat frame;
        capture >> frame;  // Captura un único frame

        if (frame.empty()) {
            cerr << "No se pudo capturar el frame." << endl;
            return -1;
        }

        string filename = "single_frame.jpg";
        bool success = imwrite(filename, frame);  // Guarda el frame

        if (success) {
            cout << "Frame guardado como " << filename << endl;
        } else {
            cerr << "Error al guardar el frame." << endl;
        }

        capture.release();  // Libera la captura
        return 0;
    }

#endif

// --------------------------------------------------------------------------------------------------------------------------------------------------------------------
