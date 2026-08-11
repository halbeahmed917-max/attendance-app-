import 'package:flutter/material.dart';
import 'package:local_auth/local_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'نظام الحضور',
      theme: ThemeData(primarySwatch: Colors.blue, fontFamily: 'Cairo'),
      home: LoginPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _codeController = TextEditingController();
  final String serverUrl = "https://attendance-server-tby3.onrender.com";
  bool _loading = false;

  void _login() async {
    setState(()=> _loading = true);
    var url = Uri.parse('$serverUrl/api/login');
    var response = await http.post(url,
      headers: {"Content-Type": "application/json"},
      body: json.encode({'fingerprint_id': _codeController.text}),
    );
    setState(()=> _loading = false);
    
    var data = json.decode(response.body);
    if(data['status'] == 'success'){
      var prefs = await SharedPreferences.getInstance();
      await prefs.setString('employee_id', data['id'].toString());
      await prefs.setString('employee_name', data['name']);
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => CheckinPage()));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(data['message'])));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("تسجيل الدخول اول مرة")),
      body: Padding(
        padding: EdgeInsets.all(20),
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text("ادخل رقم البصمة المسجل في النظام", style: TextStyle(fontSize: 18)),
          SizedBox(height: 20),
          TextField(controller: _codeController, decoration: InputDecoration(labelText: "رقم البصمة", border: OutlineInputBorder())),
          SizedBox(height: 20),
          _loading ? CircularProgressIndicator() : ElevatedButton(onPressed: _login, child: Text("دخول وحفظ"))
        ]),
      ),
    );
  }
}

class CheckinPage extends StatefulWidget {
  @override
  _CheckinPageState createState() => _CheckinPageState();
}

class _CheckinPageState extends State<CheckinPage> {
  final LocalAuthentication auth = LocalAuthentication();
  String _message = "مرحبا";
  String _name = "";
  final String serverUrl = "https://attendance-server-tby3.onrender.com";

  @override
  void initState() {
    super.initState();
    _loadName();
  }

  _loadName() async {
    var prefs = await SharedPreferences.getInstance();
    setState(()=> _name = prefs.getString('employee_name') ?? "");
  }

  Future<void> _authenticate() async {
    bool authenticated = await auth.authenticate(localizedReason: 'ضع اصبعك لتسجيل الحضور', options: AuthenticationOptions(biometricOnly: true, stickyAuth: true));
    if (authenticated) {
      await _sendToServer();
    } else {
      setState(() => _message = "فشلت عملية البصمة");
    }
  }

  Future<void> _sendToServer() async {
    var prefs = await SharedPreferences.getInstance();
    var employeeId = prefs.getString('employee_id');
    var url = Uri.parse('$serverUrl/api/checkin_app');
    var response = await http.post(url, headers: {"Content-Type": "application/json"}, body: json.encode({'employee_id': employeeId}));
    var data = json.decode(response.body);
    setState(() => _message = data['message']);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("تسجيل الحضور")),
      body: Center(
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text("مرحبا $_name", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          SizedBox(height: 20),
          Icon(Icons.fingerprint, size: 100, color: Colors.blue),
          Text(_message, style: TextStyle(fontSize: 18)),
          SizedBox(height: 20),
          ElevatedButton(onPressed: _authenticate, child: Padding(padding: EdgeInsets.all(12), child: Text("بصمة الحضور", style: TextStyle(fontSize: 18))))
        ]),
      ),
    );
  }
}