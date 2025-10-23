import React, { useState } from "react"
import { ChevronLeft, ChevronRight, Clock, Globe } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "./avatar"
import { Button } from "./button"
import { Separator } from "./separator"
import { cn } from "@/lib/utils"

export function AppointmentScheduler({
  patientName,
  patientAvatar,
  doctorName,
  appointmentType,
  duration,
  timezone,
  availableDates = [],
  timeSlots = [],
  onDateSelect,
  onTimeSelect,
  onTimezoneChange,
  brandName = "CESFAM",
}) {
  const [selectedDate, setSelectedDate] = useState(null)
  const [selectedTime, setSelectedTime] = useState(null)
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [is24Hour, setIs24Hour] = useState(false)

  const monthNames = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
  ]

  const weekDays = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]

  const handleDateClick = (date) => {
    const dateObj = availableDates.find((d) => d.date === date)
    if (dateObj && dateObj.isAvailable) {
      setSelectedDate(date)
      setSelectedTime(null)
      // Create full Date object with current month/year being viewed
      const fullDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), date)
      if (onDateSelect) onDateSelect(fullDate)
    }
  }

  const handleTimeClick = (time) => {
    const slot = timeSlots.find((s) => s.time === time)
    if (slot && slot.isAvailable) {
      setSelectedTime(time)
      if (onTimeSelect) onTimeSelect(time)
    }
  }

  const getDaysInMonth = () => {
    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    const firstDay = new Date(year, month, 1).getDay()
    const daysInMonth = new Date(year, month + 1, 0).getDate()

    const days = []
    for (let i = 0; i < firstDay; i++) {
      days.push(null)
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i)
    }
    return days
  }

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))
  }

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))
  }

  const formatTime = (time) => {
    if (is24Hour) {
      const parts = time.split(" ")
      const timePart = parts[0]
      return timePart
    }
    return time
  }

  return (
    <div className="flex h-full flex-col gap-8 rounded-2xl border bg-white p-8 shadow-sm lg:flex-row">
      {/* Left Panel */}
      <div className="flex w-full flex-col gap-6 lg:w-80">
        <div className="flex items-center gap-3">
          <Avatar className="h-12 w-12">
            <AvatarImage src={patientAvatar} alt={patientName} />
            <AvatarFallback className="bg-blue-100 text-blue-600">
              {patientName && patientName.split(" ").map((n) => n[0]).join("")}
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 className="text-base font-semibold text-gray-900">{patientName}</h3>
            <p className="text-sm text-gray-500">{brandName}</p>
          </div>
        </div>

        <Separator />

        <div className="space-y-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Doctor
            </p>
            <p className="mt-1 text-sm font-medium text-gray-900">{doctorName}</p>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              Tipo de Atención
            </p>
            <p className="mt-1 text-sm font-medium text-gray-900">{appointmentType}</p>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            <span>{duration}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Globe className="h-4 w-4" />
            <select
              value={timezone}
              onChange={(e) => onTimezoneChange && onTimezoneChange(e.target.value)}
              className="border-none bg-transparent text-sm focus:outline-none focus:ring-0"
            >
              <option value="America/Santiago">Santiago, Chile (GMT-3)</option>
            </select>
          </div>
        </div>
      </div>

      <Separator orientation="vertical" className="hidden lg:block" />

      {/* Center Panel - Calendar */}
      <div className="flex flex-1 flex-col">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
          </h2>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" onClick={previousMonth} className="h-8 w-8">
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={nextMonth} className="h-8 w-8">
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="grid flex-1 grid-cols-7 gap-2">
          {weekDays.map((day) => (
            <div key={day} className="text-center text-xs font-medium text-gray-500">
              {day}
            </div>
          ))}
          {getDaysInMonth().map((day, index) => {
            const dateObj = availableDates.find((d) => d.date === day)
            const isAvailable = dateObj && dateObj.isAvailable
            const isSelected = selectedDate === day

            return (
              <button
                key={index}
                onClick={() => day && handleDateClick(day)}
                disabled={!day || !isAvailable}
                className={cn(
                  "aspect-square rounded-lg text-sm transition-all hover:scale-105",
                  !day && "invisible",
                  day && !isAvailable && "cursor-not-allowed text-gray-300",
                  day && isAvailable && !isSelected && "bg-gray-50 text-gray-900 hover:bg-gray-100",
                  isSelected && "bg-blue-600 text-white hover:bg-blue-700"
                )}
              >
                {day}
              </button>
            )
          })}
        </div>
      </div>

      <Separator orientation="vertical" className="hidden lg:block" />

      {/* Right Panel - Time Slots */}
      <div className="w-full lg:w-72">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">
            {selectedDate ? selectedDate + " " + monthNames[currentMonth.getMonth()] : "Horarios"}
          </h3>
          <button
            onClick={() => setIs24Hour(!is24Hour)}
            className="text-xs text-blue-600 hover:text-blue-700"
          >
            {is24Hour ? "12h" : "24h"}
          </button>
        </div>

        <div className="space-y-2">
          {timeSlots.length === 0 && (
            <p className="text-center text-sm text-gray-500">
              Selecciona una fecha para ver horarios disponibles
            </p>
          )}
          {timeSlots.map((slot) => (
            <button
              key={slot.time}
              onClick={() => handleTimeClick(slot.time)}
              disabled={!slot.isAvailable}
              className={cn(
                "w-full rounded-lg border px-4 py-2.5 text-sm font-medium transition-all hover:scale-[1.02]",
                !slot.isAvailable && "cursor-not-allowed bg-gray-50 text-gray-400",
                slot.isAvailable && selectedTime !== slot.time && "border-gray-200 bg-white text-gray-900 hover:border-blue-300 hover:bg-blue-50",
                selectedTime === slot.time && "border-blue-600 bg-blue-50 text-blue-600"
              )}
            >
              {formatTime(slot.time)}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
