import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../constants/app_colors.dart';
import '../../providers/predict_provider.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/model_not_ready_dialog.dart';
import '../../widgets/not_banana_leaf_dialog.dart';
import '../../widgets/prediction_detail_dialog.dart';
import '../profile/edit_profile_screen.dart';

class PredictScreen extends StatefulWidget {
  final VoidCallback? onBack;

  const PredictScreen({
    super.key,
    this.onBack,
  });

  @override
  State<PredictScreen> createState() => _PredictScreenState();
}

class _PredictScreenState extends State<PredictScreen> {
  File? _selectedImageFile;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    // Periksa status kesiapan model saat halaman dibuka
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<PredictProvider>(context, listen: false).checkModelReadiness();
    });
  }

  Future<void> _pickImage(ImageSource source) async {
    final predictProvider = Provider.of<PredictProvider>(context, listen: false);
    if (!predictProvider.isModelReady) {
      showModelNotReadyDialog(
        context: context,
        message: predictProvider.modelStatusMessage,
      );
      return;
    }

    try {
      final picked = await _picker.pickImage(
        source: source,
        maxWidth: 1280,
        maxHeight: 1280,
        imageQuality: 88,
      );

      if (picked != null) {
        setState(() {
          _selectedImageFile = File(picked.path);
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal memilih gambar: $e'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  void _handlePredict() async {
    if (_selectedImageFile == null) return;

    final provider = Provider.of<PredictProvider>(context, listen: false);

    // Cek apakah model belum siap sebelum memproses
    if (!provider.isModelReady) {
      showModelNotReadyDialog(
        context: context,
        message: provider.modelStatusMessage,
      );
      return;
    }

    final result = await provider.predict(_selectedImageFile!.path);

    if (!mounted) return;

    if (result != null) {
      showPredictionDetailDialog(
        context: context,
        prediction: result,
        localImagePath: _selectedImageFile?.path,
        onDeleted: () {
          setState(() {
            _selectedImageFile = null;
          });
        },
      );
    } else if (provider.isModelNotReadyError ||
        (provider.errorMessage != null &&
            (provider.errorMessage!.toLowerCase().contains('belum aktif') ||
                provider.errorMessage!.toLowerCase().contains('belum di load') ||
                provider.errorMessage!.toLowerCase().contains('belum dimuat') ||
                provider.errorMessage!.toLowerCase().contains('belum siap')))) {
      // Pop-up jika model belum di-load sesuai pesan backend
      showModelNotReadyDialog(
        context: context,
        message: provider.modelStatusMessage ?? provider.errorMessage,
      );
    } else if (provider.isNotBananaLeaf) {
      // Tampilkan popup "Peringatan Gambar" jika bukan daun pisang (sesuai wireframe)
      showNotBananaLeafDialog(
        context: context,
        onRetry: () {
          setState(() {
            _selectedImageFile = null;
          });
          provider.reset();
        },
      );
    } else if (provider.errorMessage != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.warning_amber_rounded, color: Colors.white),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  provider.errorMessage!,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          backgroundColor: AppColors.error,
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 4),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final predictProvider = Provider.of<PredictProvider>(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios_new_rounded,
            color: AppColors.textPrimary,
            size: 20,
          ),
          onPressed: () {
            if (widget.onBack != null) {
              widget.onBack!();
            } else if (Navigator.canPop(context)) {
              Navigator.pop(context);
            }
          },
        ),
        title: const Text(
          'Prediksi Baru',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
            color: AppColors.textPrimary,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        actions: [
          IconButton(
            icon: Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppColors.primaryLight,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.settings_outlined,
                color: AppColors.primaryDark,
                size: 22,
              ),
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const EditProfileScreen(),
                ),
              );
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // ==========================================
              // 1. FRAME GAMBAR BESAR (Sesuai Wireframe)
              // ==========================================
              Container(
                width: double.infinity,
                constraints: BoxConstraints(
                  maxWidth: size.width > 420 ? 380 : double.infinity,
                  maxHeight: 320,
                  minHeight: 260,
                ),
                decoration: BoxDecoration(
                  color: AppColors.cardSurface,
                  borderRadius: BorderRadius.circular(28), // Sudut melengkung lebar
                  border: Border.all(
                    color: AppColors.cardBorder,
                    width: 1.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(28),
                  child: _selectedImageFile != null
                      ? Stack(
                          fit: StackFit.expand,
                          children: [
                            Image.file(
                              _selectedImageFile!,
                              fit: BoxFit.cover,
                            ),
                            Positioned(
                              top: 12,
                              right: 12,
                              child: GestureDetector(
                                onTap: () {
                                  setState(() {
                                    _selectedImageFile = null;
                                  });
                                  predictProvider.reset();
                                },
                                child: Container(
                                  padding: const EdgeInsets.all(6),
                                  decoration: BoxDecoration(
                                    color: Colors.black.withOpacity(0.6),
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.close_rounded,
                                    color: Colors.white,
                                    size: 18,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        )
                      : Center(
                          // Ilustrasi Gambar Sesuai Wireframe Mas Yoga
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Container(
                                padding: const EdgeInsets.all(24),
                                decoration: BoxDecoration(
                                  color: AppColors.primaryMuted,
                                  borderRadius: BorderRadius.circular(24),
                                ),
                                child: const Icon(
                                  Icons.image_outlined,
                                  size: 110,
                                  color: AppColors.primaryDark,
                                ),
                              ),
                              const SizedBox(height: 12),
                              const Text(
                                'Belum ada foto yang dipilih',
                                style: TextStyle(
                                  fontSize: 13,
                                  color: AppColors.textSecondary,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                ),
              ),

              const SizedBox(height: 20),

              // ==========================================
              // 2. KONTAINER AKSI (Galeri & Ambil Foto)
              // ==========================================
              Container(
                width: double.infinity,
                constraints: BoxConstraints(
                  maxWidth: size.width > 420 ? 380 : double.infinity,
                ),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 22),
                decoration: BoxDecoration(
                  color: AppColors.cardSurface,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: AppColors.cardBorder,
                    width: 1.2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.03),
                      blurRadius: 16,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    // Teks Petunjuk Sesuai Wireframe
                    const Text(
                      'Pilih foto tanaman untuk prediksi hasil.',
                      style: TextStyle(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),

                    const SizedBox(height: 20),

                    // Baris Tombol Galeri dan Ambil Foto
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // 1. Tombol Galeri
                        GestureDetector(
                          onTap: () => _pickImage(ImageSource.gallery),
                          child: Column(
                            children: [
                              Container(
                                width: 62,
                                height: 62,
                                decoration: BoxDecoration(
                                  color: AppColors.inputBackground,
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: AppColors.cardBorder,
                                    width: 1.5,
                                  ),
                                ),
                                child: const Center(
                                  child: Icon(
                                    Icons.photo_library_outlined,
                                    size: 28,
                                    color: AppColors.textPrimary,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'Galeri',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                            ],
                          ),
                        ),

                        // 2. Tombol Ambil Foto (Shutter Button Kamera dengan Ring Ganda)
                        GestureDetector(
                          onTap: () => _pickImage(ImageSource.camera),
                          child: Column(
                            children: [
                              Container(
                                width: 78,
                                height: 78,
                                padding: const EdgeInsets.all(5),
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: AppColors.primary,
                                    width: 3,
                                  ),
                                ),
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: AppColors.cardSurface,
                                    shape: BoxShape.circle,
                                    boxShadow: [
                                      BoxShadow(
                                        color: AppColors.primary.withOpacity(0.2),
                                        blurRadius: 8,
                                        offset: const Offset(0, 2),
                                      ),
                                    ],
                                  ),
                                  child: const Center(
                                    child: Icon(
                                      Icons.camera_alt_rounded,
                                      size: 34,
                                      color: AppColors.primary,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 6),
                              const Text(
                                'Ambil Foto',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.primaryForest,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // ==========================================
              // 3. TOMBOL PROSES PREDIKSI (Jika Gambar Sudah Terpilih)
              // ==========================================
              if (_selectedImageFile != null)
                Container(
                  constraints: BoxConstraints(
                    maxWidth: size.width > 420 ? 380 : double.infinity,
                  ),
                  child: CustomButton(
                    text: 'Prediksi Sekarang',
                    icon: const Icon(Icons.auto_awesome, color: Colors.white, size: 20),
                    isLoading: predictProvider.isLoading,
                    backgroundColor: AppColors.primary,
                    onPressed: _handlePredict,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

