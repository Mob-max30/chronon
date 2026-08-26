"use client";

import React, { useState, useEffect } from "react";
import { Room } from "@/types";
import { getRooms, createRoom, updateRoom, deleteRoom } from "@/lib/api";
import { Building2, Plus, Edit2, Trash2, CheckCircle2, XCircle, Users, Layers } from "lucide-react";

export function RoomManager() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);

  // Form State
  const [name, setName] = useState("");
  const [building, setBuilding] = useState("");
  const [capacity, setCapacity] = useState(60);
  const [roomType, setRoomType] = useState("LECTURE_HALL");
  const [isActive, setIsActive] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRooms = async () => {
    setLoading(true);
    try {
      const data = await getRooms();
      setRooms(data);
    } catch (err: any) {
      setError(err.message || "Failed to load rooms");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRooms();
  }, []);

  const openCreateModal = () => {
    setEditingRoom(null);
    setName("");
    setBuilding("");
    setCapacity(60);
    setRoomType("LECTURE_HALL");
    setIsActive(true);
    setError(null);
    setIsModalOpen(true);
  };

  const openEditModal = (room: Room) => {
    setEditingRoom(room);
    setName(room.name);
    setBuilding(room.building || "");
    setCapacity(room.capacity);
    setRoomType(room.room_type || "LECTURE_HALL");
    setIsActive(room.is_active);
    setError(null);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Room name / number is required (e.g. LH-101)");
      return;
    }
    if (capacity <= 0) {
      setError("Room capacity must be a positive integer greater than 0");
      return;
    }

    try {
      if (editingRoom) {
        await updateRoom(editingRoom.id, {
          name,
          building,
          capacity,
          room_type: roomType,
          is_active: isActive,
        });
      } else {
        await createRoom({
          institution_id: 1,
          name,
          building,
          capacity,
          room_type: roomType,
          is_active: isActive,
        });
      }
      setIsModalOpen(false);
      loadRooms();
    } catch (err: any) {
      setError(err.message || "Failed to save room");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this classroom?")) return;
    try {
      await deleteRoom(id);
      loadRooms();
    } catch (err: any) {
      alert(err.message || "Failed to delete room");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-blue-400" /> Classrooms & Lecture Halls
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Physical classroom spaces. Room capacity is the single authoritative source for section size calculation.
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-blue-600/20"
        >
          <Plus className="w-4 h-4" /> Add Classroom
        </button>
      </div>

      {/* Grid of Rooms */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading classroom resources...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rooms.map((room) => (
            <div
              key={room.id}
              className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 hover:border-slate-700 transition flex flex-col justify-between space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white tracking-wide">{room.name}</h3>
                    {room.is_active ? (
                      <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full font-medium">
                        <CheckCircle2 className="w-3 h-3" /> Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full font-medium">
                        <XCircle className="w-3 h-3" /> Inactive
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{room.building || "Main Campus"}</p>
                </div>
                <span className="text-[10px] font-mono font-bold text-blue-400 bg-blue-500/10 px-2 py-1 rounded-md border border-blue-500/20">
                  {room.room_type}
                </span>
              </div>

              {/* Room Stats */}
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80 text-xs">
                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50 flex items-center gap-2">
                  <Users className="w-4 h-4 text-blue-400" />
                  <div>
                    <div className="text-[10px] text-slate-500 font-medium">Capacity</div>
                    <div className="font-bold text-slate-200">{room.capacity} seats</div>
                  </div>
                </div>
                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-indigo-400" />
                  <div>
                    <div className="text-[10px] text-slate-500 font-medium">Type</div>
                    <div className="font-bold text-slate-200 truncate">{room.room_type.replace("_", " ")}</div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  onClick={() => openEditModal(room)}
                  className="p-2 rounded-lg border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
                  title="Edit Room"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => handleDelete(room.id)}
                  className="p-2 rounded-lg border border-red-900/30 hover:bg-red-500/10 text-red-400 hover:text-red-300 transition"
                  title="Delete Room"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white">
                {editingRoom ? "Edit Classroom" : "Create Classroom"}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Room Name / Number <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. LH-101, Room 304"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">Building / Block</label>
                <input
                  type="text"
                  value={building}
                  onChange={(e) => setBuilding(e.target.value)}
                  placeholder="e.g. Main Academic Block, North Wing"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1.5">
                    Seating Capacity <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={capacity}
                    onChange={(e) => setCapacity(parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-blue-500"
                    required
                  />
                  <p className="text-[10px] text-slate-500 mt-1">Source for section division</p>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1.5">Room Type</label>
                  <select
                    value={roomType}
                    onChange={(e) => setRoomType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="LECTURE_HALL">Lecture Hall</option>
                    <option value="SEMINAR_HALL">Seminar Hall</option>
                    <option value="AUDITORIUM">Auditorium</option>
                    <option value="DRAWING_HALL">Drawing Hall</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="isActive"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                  className="rounded border-slate-800 bg-slate-950 text-blue-600 focus:ring-0"
                />
                <label htmlFor="isActive" className="text-slate-300 font-medium">
                  Room is active for scheduling
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold shadow-lg shadow-blue-600/20 transition"
                >
                  {editingRoom ? "Save Changes" : "Create Room"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
