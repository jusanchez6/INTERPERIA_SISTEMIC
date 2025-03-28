#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>
#include <chrono>
#include <thread>

using namespace cv;
using namespace std;

enum CaptureMode { SINGLE_SHOT, MULTI_SHOT };
constexpr CaptureMode MODE = SINGLE_SHOT;  // Cambia a MULTI_SHOT para múltiples capturas
constexpr int FRAME_RATE = 23;  // Solo para MULTI_SHOT

// Función para construir el pipeline de GStreamer
string buildGStreamerPipeline(const string& device) {
    string gstFormat = "NV12";
    return "v4l2src device=" + device + 
           " ! video/x-raw,format=" + gstFormat + ",width=1920,height=1080,framerate=30/1 ! videoconvert ! appsink";
}

// Captura y guarda un solo frame
void captureSingleFrame(const string& device) {
    VideoCapture capture(buildGStreamerPipeline(device));
    if (!capture.isOpened()) {
        cerr << "Error al abrir la cámara." << endl;
        return;
    }

    Mat frame;
    capture >> frame;

    if (frame.empty()) {
        cerr << "No se pudo capturar el frame." << endl;
        return;
    }

    if (imwrite("single_frame.jpg", frame)) {
        cout << "Frame guardado como single_frame.jpg" << endl;
    } else {
        cerr << "Error al guardar el frame." << endl;
    }
}

// Captura múltiples frames y solo guarda el último
void captureMultipleFrames(const string& device) {
    VideoCapture capture(buildGStreamerPipeline(device));
    if (!capture.isOpened()) {
        cerr << "Error al abrir la cámara." << endl;
        return;
    }

    cout << "Iniciando captura a " << FRAME_RATE << " FPS. Presione Ctrl+C para detener." << endl;
    auto frameDuration = chrono::milliseconds(1000 / FRAME_RATE);

    while (true) {
        auto start_time = chrono::high_resolution_clock::now();
        
        Mat frame;
        capture >> frame;

        if (frame.empty()) {
            cerr << "No se pudo capturar el frame." << endl;
            break;
        }

        if (imwrite("current_frame.jpg", frame)) {
            cout << "Frame guardado como current_frame.jpg" << endl;
        } else {
            cerr << "Error al guardar el frame." << endl;
            break;
        }

        auto elapsed_time = chrono::high_resolution_clock::now() - start_time;
        this_thread::sleep_for(frameDuration - chrono::duration_cast<chrono::milliseconds>(elapsed_time));
    }
}

int main(int argc, char** argv) {
    if (argc != 2) {
        cerr << "Uso: " << argv[0] << " <dispositivo>\nEjemplo: " << argv[0] << " /dev/video0" << endl;
        return -1;
    }

    string device = argv[1];

    if (MODE == SINGLE_SHOT) {
        captureSingleFrame(device);
    } else {
        captureMultipleFrames(device);
    }

    return 0;
}

