import { Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import MovieDetail from "./pages/MovieDetail";
import SeatSelection from "./pages/SeatSelection";
import Checkout from "./pages/Checkout";
import MyTickets from "./pages/MyTickets";
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminComments from "./pages/AdminComments";
import AdminMovies from "./pages/AdminMovies";
import AdminShowtimes from "./pages/AdminShowtimes";
import AdminModelCompare from "./pages/AdminModelCompare";
import NotFound from "./pages/NotFound";
import Explore from "./pages/Explore";

export default function App() {
  return (
    <div className="app">
      <Header />
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/kham-pha" element={<Explore />} />
          <Route path="/phim/:id" element={<MovieDetail />} />
          <Route path="/dang-nhap" element={<Login />} />
          <Route path="/dang-ky" element={<Register />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/dat-ve/:showtimeId" element={<SeatSelection />} />
            <Route path="/xac-nhan" element={<Checkout />} />
            <Route path="/ve-cua-toi" element={<MyTickets />} />
          </Route>
          <Route element={<ProtectedRoute adminOnly />}>
            <Route path="/quan-tri/phim" element={<AdminMovies />} />
            <Route path="/quan-tri/suat-chieu" element={<AdminShowtimes />} />
            <Route path="/quan-tri/binh-luan" element={<AdminComments />} />
            <Route path="/quan-tri/so-sanh-mo-hinh" element={<AdminModelCompare />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
